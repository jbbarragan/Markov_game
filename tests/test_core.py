import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'docs'/'game'))
from core import World,Learner

class Fixed:
    def __init__(self,values): self.values=iter(values)
    def gauss(self,*args): return next(self.values)
    def random(self): return 1.

class TestEnvironment(unittest.TestCase):
    def test_initial_and_spawn(self):
        for seed in range(100):
            w=World(seed=seed)
            self.assertEqual(len(w.cans),12)
            self.assertNotIn((0,0),w.cans)
            self.assertTrue(all(0<=x<10 and 0<=y<10 for x,y in w.cans))
    def test_wait_horizon_return(self):
        w=World()
        for _ in range(110): w.step(4)
        self.assertEqual(w.t,100);self.assertEqual(w.energy,100)
        self.assertAlmostEqual(w.score,10);self.assertAlmostEqual(w.discounted,.1*(1-.95**100)/.05)
    def test_boundary_cost(self):
        w=World();w.rng=Fixed([10,0]);w.step(0)
        self.assertEqual((w.x,w.y),(0,0));self.assertEqual(w.energy,90);self.assertEqual(w.score,-.05)
    def test_slip_right(self):
        w=World();w.rng=Fixed([10,31]);w.step(0)
        self.assertEqual((w.x,w.y),(1,0))
    def test_rescue_precedes_collection(self):
        w=World();w.energy=1;w.cans[1,0]=0;w.rng=Fixed([16,0]);w.step(1)
        self.assertEqual((w.x,w.y,w.energy),(0,0,100));self.assertEqual(w.score,-3);self.assertEqual(w.caught,0);self.assertIn((1,0),w.cans)
    def test_invalid_recharge(self):
        w=World();w.x=1;self.assertFalse(w.step(5));self.assertEqual(w.t,0)
    def test_charge(self):
        w=World();w.energy=25;w.step(5);self.assertEqual(w.energy,100);self.assertEqual(w.score,0)
    def test_extended_time(self):
        w=World('extended');w.step(4,2);self.assertEqual(w.energy,99);self.assertEqual(w.score,0)
    def test_collection_reward_and_replacement(self):
        for mode,value in [('practice',1),('extended',4)]:
            w=World(mode);w.cans.pop(next(iter(w.cans)));w.cans[1,0]=2
            original=w.rng.gauss;counter=[0]
            def sample(mu,sigma):
                counter[0]+=1
                return [10,0][counter[0]-1] if counter[0]<=2 else original(mu,sigma)
            w.rng.gauss=sample
            w.step(1)
            self.assertEqual(w.score,value);self.assertEqual(w.caught,1);self.assertGreaterEqual(len(w.cans),12)
    def test_seed_reproducibility(self):
        a,b=World(seed=123),World(seed=123)
        for action in [1,2,4,0,3]*20:a.step(action);b.step(action)
        self.assertEqual(a.state(),b.state())
    def test_probabilities(self):
        w=World();w.energy=50;self.assertAlmostEqual(w.state()['alpha'],.5)
        w.energy=16;self.assertAlmostEqual(w.state()['beta'],.5)
    def test_agent_terminal_no_bootstrap(self):
        w=World();w.t=99;a=Learner();a.choose=lambda *_:4
        key=a.key(w);a.row(key)[4]=10;a.advance(w)
        self.assertAlmostEqual(a.q[key][4],10+.15*(.1-10));self.assertEqual(a.episodes,1)
    def test_agent_evaluation_frozen(self):
        w=World();a=Learner();a.choose=lambda *_:4
        a.advance(w,False);self.assertEqual(a.q,{});self.assertEqual(a.episodes,0)
        b=Learner();b.advance(World(),False);self.assertEqual(b.q,{})
    def test_practice_invariants(self):
        for seed in range(20):
            w=World(seed=seed);a=Learner(seed)
            for _ in range(100):
                a.advance(w)
                self.assertEqual(len(w.cans),12);self.assertTrue(0<w.energy<=100)
            self.assertEqual(w.t,100)

if __name__=='__main__': unittest.main()
