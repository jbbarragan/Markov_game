import csv
import io
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'docs'/'game'))
import core
from core import World,Learner,RATES

class Fixed:
    def __init__(self,values): self.values=iter(values)
    def gauss(self,*args): return next(self.values)
    def random(self): return 1.

def quiet(w):
    """Sin ruido de consumo: la descarga es exactamente tasa × tiempo."""
    w.nrng=Fixed([0]*1000)
    return w

class TestEnvironment(unittest.TestCase):
    def test_initial_and_spawn(self):
        for seed in range(100):
            w=World(seed=seed)
            self.assertEqual(len(w.cans),12)
            self.assertNotIn((0,0),w.cans)
            self.assertTrue(all(0<=x<10 and 0<=y<10 for x,y in w.cans))
    def test_boundary_and_slip(self):
        w=quiet(World(drain='1'));w.rng=Fixed([0]);w.step(0)
        self.assertEqual((w.x,w.y),(0,0));self.assertAlmostEqual(w.energy,99);self.assertEqual(w.score,-.05)
        w=quiet(World(drain='1'));w.rng=Fixed([31]);w.step(0)
        self.assertEqual((w.x,w.y),(1,0))
    def test_rescue_precedes_collection(self):
        w=quiet(World(drain='9'));w.energy=1;w.cans[1,0]=0;w.rng=Fixed([0]);w.step(1)
        self.assertEqual((w.x,w.y,w.energy),(0,0,100));self.assertEqual(w.score,-3);self.assertEqual(w.caught,0);self.assertIn((1,0),w.cans)
    def test_invalid_recharge(self):
        w=World();w.x=1;self.assertFalse(w.step(5));self.assertEqual(w.t,0)
    def test_charge_is_instant_and_never_rescues(self):
        w=quiet(World(drain='9'));w.energy=3;w.step(5)
        self.assertEqual(w.energy,100);self.assertEqual(w.score,0);self.assertEqual(w.rescues,0)
    def test_extended_time(self):
        w=quiet(World('extended',drain='2'));w.step(4,2)
        self.assertAlmostEqual(w.energy,96);self.assertEqual(w.score,0)
    def test_collection_reward_and_replacement(self):
        for mode,value in [('practice',1),('extended',4)]:
            w=World(mode);w.cans.pop(next(iter(w.cans)));w.cans[1,0]=2
            original=w.rng.gauss;counter=[0]
            def sample(mu,sigma):
                counter[0]+=1
                return 0 if counter[0]==1 else original(mu,sigma)
            w.rng.gauss=sample
            w.step(1)
            self.assertEqual(w.score,value);self.assertEqual(w.caught,1);self.assertGreaterEqual(len(w.cans),12)
    def test_seed_reproducibility(self):
        for drain in ['random','mixed','6']:
            a,b=World(seed=123,drain=drain),World(seed=123,drain=drain)
            for action in [1,2,4,0,3]*20:a.step(action);b.step(action)
            self.assertEqual(a.state(),b.state())

class TestTimeDrain(unittest.TestCase):
    def test_constant_rates_are_linear_in_time(self):
        for r in RATES:
            w=quiet(World(drain=str(int(r))))
            for n in range(1,6):
                w.step(4)
                self.assertAlmostEqual(w.energy,100-r*n)
    def test_drain_depends_on_time_not_on_action(self):
        a,b=quiet(World(seed=5,drain='4')),quiet(World(seed=5,drain='4'))
        for _ in range(10):
            a.step(4);b.step(1)
        self.assertAlmostEqual(a.energy,b.energy);self.assertAlmostEqual(a.energy,60)
    def test_slow_rate_lasts_a_whole_episode(self):
        w=quiet(World(drain='1'))
        for _ in range(99): w.step(4)
        self.assertEqual(w.rescues,0);self.assertAlmostEqual(w.energy,1)
    def test_waiting_still_costs_energy(self):
        w=quiet(World(drain='9'))
        for _ in range(12): w.step(4)
        self.assertEqual(w.rescues,1)
    def test_mixed_profile_is_piecewise_and_additive(self):
        w=World(seed=9,drain='mixed');w.rate_at(120)
        rates=[r for _,r in w.segments]
        self.assertTrue(all(r in RATES for r in rates));self.assertTrue(all(p!=q for p,q in zip(rates,rates[1:])))
        self.assertGreater(len(set(rates)),1)
        self.assertAlmostEqual(w.integrate(0,10)+w.integrate(10,57.5),w.integrate(0,57.5))
        self.assertAlmostEqual(w.integrate(0,1),w.rate_at(0))
    def test_random_profile_varies_between_games_and_is_seeded(self):
        profiles={World(seed=s).profile for s in range(60)}
        self.assertGreaterEqual(len(profiles),5)
        self.assertEqual(World(seed=7).profile,World(seed=7).profile)
    def test_forced_option_wins_over_random(self):
        for opt in ['1','2','4','6','9','mixed']: self.assertEqual(World(seed=3,drain=opt).profile,opt)
    def test_probabilities_follow_current_rate(self):
        w=World(drain='2');w.energy=42;self.assertEqual(w.state()['alpha'],0)
        w.energy=2;self.assertEqual(w.state()['beta'],0)
    def test_balance_adds_up_to_score(self):
        for seed in range(10):
            w=World(seed=seed);a=Learner(seed)
            while w.t<100: a.advance(w)
            self.assertAlmostEqual(sum(w.balance.values()),w.score);self.assertEqual(sum(w.counts.values()),100)

class TestAgent(unittest.TestCase):
    def test_agent_terminal_no_bootstrap(self):
        w=World();w.t=99;a=Learner();a.choose=lambda *_:4
        key=a.key(w);a.row(key)[4]=10;a.advance(w)
        self.assertAlmostEqual(a.q[key][4],10+.15*(.1-10));self.assertEqual(a.episodes,1)
    def test_agent_evaluation_frozen(self):
        w=World();a=Learner();a.choose=lambda *_:4
        a.advance(w,False);self.assertEqual(a.q,{});self.assertEqual(a.episodes,0)
        b=Learner();b.advance(World(),False);self.assertEqual(b.q,{})
    def test_practice_invariants(self):
        for seed,drain in zip(range(21),['random','1','2','4','6','9','mixed']*3):
            w=World(seed=seed,drain=drain);a=Learner(seed)
            for _ in range(100):
                a.advance(w)
                self.assertEqual(len(w.cans),12);self.assertTrue(0<w.energy<=100)
            self.assertEqual(w.t,100)
    def test_telemetry_and_balance_csv(self):
        a=Learner(1)
        for seed in range(3):
            w=World(seed=seed)
            while w.t<100: a.advance(w)
        w=World(seed=99)
        while w.t<100: a.advance(w,False)
        tele=list(csv.DictReader(io.StringIO(a.csv('telemetry')[0])))
        self.assertEqual(len(tele),400);self.assertEqual(list(tele[0].keys()),core.TELEMETRY_COLUMNS)
        self.assertEqual({r['phase'] for r in tele},{'entrenamiento','evaluacion'})
        self.assertTrue(all(r['rate'] and r['reward_type'] for r in tele))
        bal=list(csv.DictReader(io.StringIO(a.csv('balance')[0])))
        self.assertEqual(len(bal),4);self.assertEqual(list(bal[0].keys()),core.BALANCE_COLUMNS)
        for r in bal:
            parts=sum(float(r['reward_'+k]) for k in core.BALANCE_KEYS)
            self.assertAlmostEqual(parts,float(r['score']),places=2)
        self.assertEqual(a.episodes,3);self.assertEqual(len(a.eval_history),1)
    def test_dispatch_reset_and_csv(self):
        core.dispatch(json.dumps(dict(op='reset',mode='practice',seed=1,fresh=True,drain='9')))
        out=json.loads(core.dispatch(json.dumps(dict(op='train',count=2))))
        self.assertEqual(out['agent']['episodes'],2);self.assertEqual(out['state']['drain_option'],'9')
        res=json.loads(core.dispatch(json.dumps(dict(op='csv',kind='balance'))))
        self.assertEqual(res['rows'],2);self.assertIn('reward_latas',res['csv'])



class TestIndependentClock(unittest.TestCase):
    def test_many_moves_same_time_as_idle(self):
        for mode in ['practice','extended']:
            idle=World(mode,drain='4');moving=World(mode,drain='4')
            idle.step(None,2,record=False)
            for _ in range(20):moving.step(0,.1,record=False)
            self.assertAlmostEqual(idle.energy,92)
            self.assertAlmostEqual(moving.energy,idle.energy)
            self.assertEqual(idle.t,0)
            self.assertEqual(idle.score,0)
            self.assertEqual(idle.log,[])
    def test_idle_rescue_and_no_movement_cost(self):
        w=World(drain='9');w.energy=.5
        w.step(None,.1,record=False)
        self.assertEqual(w.rescues,1);self.assertEqual(w.score,-3)
        self.assertEqual(w.energy,100);self.assertEqual(w.t,0)
        for _ in range(20):w.step(0,0,record=False)
        self.assertEqual(w.energy,100)
    def test_agent_duration_is_five_decisions_per_second(self):
        w=World(drain='1');a=Learner();a.choose=lambda *_:4
        for _ in range(100):a.advance(w)
        self.assertAlmostEqual(w.elapsed,20)
        self.assertAlmostEqual(w.energy,80)

if __name__=='__main__': unittest.main()
