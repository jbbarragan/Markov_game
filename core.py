"""Can Finder 5000: entorno independiente de la interfaz, Python estándar."""
import csv
import io
import json
import math
import random

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
NAMES = ['Norte', 'Este', 'Sur', 'Oeste', 'Esperar', 'Recargar']
VALUES = [1., 2., 4.]

# Desgaste de batería: función del TIEMPO, no del movimiento (puntos porcentuales por segundo).
RATES = [1., 2., 4., 6., 9.]
DRAIN_OPTIONS = ['0.5', 'random', '1', '2', '4', '6', '9', 'mixed']
NOISE = 0.0            # descarga exacta por tiempo: independiente de cuántas acciones se ejecuten
SEGMENT_SECONDS = (6, 15)   # duración de cada tramo en el perfil intercalado
BALANCE_KEYS = ['latas', 'movimiento', 'espera', 'rescates', 'recarga']

TELEMETRY_COLUMNS = ['episode', 'phase', 'turn', 'action', 'explore', 'epsilon', 'x0', 'y0', 'x', 'y',
                     'energy0', 'energy', 'rate', 'drain', 'angle', 'reward', 'reward_type', 'score',
                     'discounted', 'rescue', 'dt', 'elapsed', 'q_before', 'td_error', 'seed', 'profile']
BALANCE_COLUMNS = ['episode', 'phase', 'seed', 'mode', 'profile', 'steps', 'elapsed', 'score', 'discounted',
                   'caught', 'rescues', 'mean_rate_pct_s', 'reward_latas', 'reward_movimiento',
                   'reward_espera', 'reward_rescates', 'reward_recarga', 'n_latas', 'n_movimiento',
                   'n_espera', 'n_rescates', 'n_recarga', 'epsilon']


class World:
    def __init__(self, mode='practice', seed=42, drain='1', slip=True):
        self.slip = bool(slip)
        self.mode, self.seed = mode, int(seed)
        self.rng = random.Random(self.seed)                    # latas y derrape
        self.prng = random.Random(self.seed * 1000003 + 17)    # perfil de desgaste
        self.nrng = random.Random(self.seed * 7919 + 101)      # ruido del consumo
        self.x = self.y = self.t = self.caught = self.rescues = 0
        self.energy = 100.
        self.score = self.discounted = self.elapsed = self.drain_total = 0.
        self.balance = {k: 0. for k in BALANCE_KEYS}
        self.counts = {k: 0 for k in BALANCE_KEYS}
        self.cans = {}
        self.log = []
        self.drain_opt = str(drain) if str(drain) in DRAIN_OPTIONS else 'random'
        self._init_drain()
        self.last = dict(message='Listo en la estación. Batería al 100%. Desgaste: ' + self.profile_label(),
                         drain=0., angle=0., reward=0., rescue=False)
        for _ in range(12): self.spawn()

    # ---------- desgaste en función del tiempo ----------
    def _init_drain(self):
        opt = self.drain_opt
        if opt == 'random': opt = self.prng.choice(['1', '2', '4', '6', '9', 'mixed'])
        self.profile = opt
        self.segments = []   # lista de (fin_del_tramo_en_s, tasa_%/s)
        if opt == 'mixed': self._extend(0.)
        else: self.segments = [(math.inf, float(opt))]

    def _extend(self, until):
        while not self.segments or self.segments[-1][0] < until:
            start = self.segments[-1][0] if self.segments else 0.
            prev = self.segments[-1][1] if self.segments else None
            rate = self.prng.choice([r for r in RATES if r != prev])
            self.segments.append((start + self.prng.randint(*SEGMENT_SECONDS), rate))

    def rate_at(self, t):
        """Tasa instantánea de descarga (%/s) en el segundo t de simulación."""
        if self.profile == 'mixed': self._extend(t + 1.)
        for end, rate in self.segments:
            if t < end: return rate
        return self.segments[-1][1]

    def integrate(self, a, b):
        """Descarga media (%) acumulada entre a y b: integral de la tasa."""
        if self.profile == 'mixed': self._extend(b)
        total, start = 0., 0.
        for end, rate in self.segments:
            lo, hi = max(a, start), min(b, end)
            if hi > lo: total += (hi - lo) * rate
            start = end
            if start >= b: break
        return total

    def profile_label(self):
        return 'intercalado 1–9 %/s' if self.profile == 'mixed' else '%g %%/s' % float(self.profile)

    def autonomy(self):
        """Segundos de batería restantes si la tasa actual se mantuviera."""
        return self.energy / self.rate_at(self.elapsed)

    # ---------- latas ----------
    def spawn(self):
        # Rechazo: normal bivariada discretizada, truncada al tablero y celdas libres.
        for _ in range(10000):
            x, y = round(self.rng.gauss(6, 2)), round(self.rng.gauss(6, 2))
            if 0 <= x < 10 and 0 <= y < 10 and (x,y) not in self.cans and (x,y) not in [(0,0),(self.x,self.y)]:
                self.cans[x,y] = self.rng.randrange(3)
                return
        raise RuntimeError('No se encontró una celda libre')

    def actions(self):
        return list(range(6 if (self.x,self.y)==(0,0) else 5))

    # ---------- transición ----------
    def step(self, action, dt=1., record=True):
        if self.t >= 100 or (action is not None and action not in self.actions()): return False
        x0, y0, e0 = self.x, self.y, self.energy
        dt = max(0., float(dt))
        if not math.isfinite(dt): raise ValueError("dt debe ser finito")
        rate0 = self.rate_at(self.elapsed)
        mean_drain = self.integrate(self.elapsed, self.elapsed + dt)
        self.elapsed += dt
        angle = reward = 0.
        message, kind = (NAMES[action], 'recarga') if action is not None else ('Reloj activo · descarga por tiempo', 'espera')
        # La batería baja con el tiempo, haga lo que haga el robot. La recarga es instantánea.
        drain = 0. if action == 5 else mean_drain
        if action is not None and action < 4:
            angle = self.rng.gauss(0, 25) if self.slip else 0.
            direction = (action + (1 if angle > 30 else -1 if angle < -30 else 0)) % 4
            dx, dy = DIRS[direction]
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < 10 and 0 <= ny < 10: self.x, self.y = nx, ny
            else: message += ' · Colisión con el borde'
            if abs(angle)>30: message += ' · ¡Patinó a la '+('derecha!' if angle>0 else 'izquierda!')
            reward, kind = -.05, 'movimiento'
        elif action == 4:
            reward, kind = (.1 if self.mode == 'practice' else 0.), 'espera'
            message = 'Esperar · ' + ('+0.10 · ' if self.mode == 'practice' else '') + 'la batería sigue bajando'
        self.energy -= drain
        self.drain_total += drain
        rescue = self.energy <= 0
        if rescue:
            self.x = self.y = 0
            self.energy = 100.
            self.rescues += 1
            reward, kind = -3., 'rescates'
            message = 'BATERÍA AGOTADA · Rescate −3.00 · Regreso a la base'
        elif action == 5:
            self.energy = 100.
            message = 'Recarga completa · 100%'
        elif action is not None and action < 4 and (self.x,self.y) in self.cans:
            color = self.cans.pop((self.x,self.y))
            reward = 1. if self.mode=='practice' else VALUES[color]
            kind = 'latas'
            self.caught += 1
            self.spawn()
            message += ' · Lata +'+str(reward)
        if self.mode=='extended' and len(self.cans)<20 and self.rng.random() < 1-math.exp(-dt/8): self.spawn()
        self.score += reward
        self.discounted += .95**self.t * reward
        self.balance[kind] += reward
        if action is not None or rescue: self.counts[kind] += 1
        if action is not None: self.t += 1
        if action is None and not rescue:
            self.last = dict(self.last, rescue=False)
        else:
            self.last = dict(message=message, drain=drain, angle=angle, reward=reward, rescue=rescue, old=[x0,y0])
        if record: self.log.append(dict(turn=self.t, action=NAMES[action] if action is not None else 'Reloj', x0=x0,y0=y0,energy0=e0,x=self.x,y=self.y,energy=self.energy,
                             rate=rate0,drain=drain,angle=angle,reward=reward,reward_type=kind,score=self.score,
                             discounted=self.discounted,rescue=rescue,dt=dt,elapsed=self.elapsed,
                             seed=self.seed,profile=self.profile))
        return True

    def summary(self):
        s = dict(seed=self.seed, mode=self.mode, drain_option=self.drain_opt, profile=self.profile, steps=self.t,
                 elapsed=self.elapsed, score=self.score, discounted=self.discounted, caught=self.caught,
                 rescues=self.rescues, mean_rate_pct_s=self.drain_total / self.elapsed if self.elapsed else 0.)
        s.update({'reward_' + k: v for k, v in self.balance.items()})
        s.update({'n_' + k: v for k, v in self.counts.items()})
        return s

    def state(self):
        e=self.energy
        phi=lambda z: .5*(1+math.erf(z/math.sqrt(2)))
        mu=self.integrate(self.elapsed, self.elapsed + 1.)
        sigma=max(1e-9, NOISE*mu)
        return dict(slip=self.slip,mode=self.mode,seed=self.seed,x=self.x,y=self.y,t=self.t,energy=e,high=e>40,score=self.score,discounted=self.discounted,caught=self.caught,rescues=self.rescues,cans=[[x,y,c] for (x,y),c in self.cans.items()],last=self.last,elapsed=self.elapsed,
                    alpha=float(e-mu>40) if e>40 else None,beta=float(e-mu>0) if e<=40 else None,done=self.t>=100,
                    rate=self.rate_at(self.elapsed),profile=self.profile,profile_label=self.profile_label(),drain_option=self.drain_opt,
                    autonomy=self.autonomy(),balance=self.balance,counts=self.counts)


class Learner:
    """Q-learning tabular con agregación de estado explícita; Q inicial cero."""
    def __init__(self, seed=42):
        self.rng=random.Random(seed)
        self.q={}
        self.episodes=0
        self.history=[]        # episodios de entrenamiento (todos)
        self.eval_history=[]   # episodios de evaluación (sin explorar ni aprender)
        self.telemetry=[]      # filas por paso (se conservan las más recientes)
        self.explorations=self.exploitations=0
        self.last_explored=False

    @property
    def epsilon(self): return max(.05, .995**self.episodes)

    def key(self,w):
        target=min(w.cans, key=lambda p:(abs(p[0]-w.x)+abs(p[1]-w.y),p))
        # Autonomía = segundos de batería a la tasa actual (observable): reúne carga y desgaste en una sola variable.
        return (w.x,w.y,min(11,int(w.autonomy()//4)),target[0]-w.x,target[1]-w.y,w.cans[target],(99-w.t)//10)

    def row(self,key): return self.q.setdefault(key,[0.]*6)

    def choose(self,w,explore=True):
        actions=w.actions()
        self.last_explored=False
        if explore and self.rng.random()<self.epsilon:
            self.explorations+=1
            self.last_explored=True
            return self.rng.choice(actions)
        if explore: self.exploitations+=1
        row=self.row(self.key(w)) if explore else self.q.get(self.key(w),[0.]*6); best=max(row[a] for a in actions)
        return self.rng.choice([a for a in actions if row[a]==best])

    def advance(self,w,learn=True):
        key=self.key(w); a=self.choose(w,learn)
        explored=self.last_explored
        eps=self.epsilon if learn else 0.
        q_before=self.q.get(key,[0.]*6)[a]
        episode=self.episodes+1 if learn else len(self.eval_history)+1
        w.step(a,.2)
        td=None
        if learn:
            target=w.last['reward']
            if not w.state()['done']: target+=.95*max(self.row(self.key(w))[b] for b in w.actions())
            row=self.row(key); td=target-row[a]; row[a]+=.15*td
        if w.log:
            w.log[-1].update(episode=episode,phase='entrenamiento' if learn else 'evaluacion',explore=int(explored),
                             epsilon=eps,q_before=q_before,td_error=td)
            self.telemetry.append(w.log[-1])
            if len(self.telemetry)>40000: del self.telemetry[:5000]
        if w.t==100:
            row=w.summary(); row.update(episode=episode,epsilon=eps)
            if learn:
                self.episodes+=1
                row['phase']='entrenamiento'
                self.history.append(row)
            else:
                row['phase']='evaluacion'
                self.eval_history.append(row)

    def csv(self,kind):
        """Telemetría paso a paso o balance de recompensas por episodio, en CSV."""
        cols,rows=(TELEMETRY_COLUMNS,self.telemetry) if kind=='telemetry' else (BALANCE_COLUMNS,sorted(self.history+self.eval_history,key=lambda r:(r['phase'],r['episode'])))
        out=io.StringIO(); wr=csv.DictWriter(out,fieldnames=cols,extrasaction='ignore',restval='',lineterminator='\n'); wr.writeheader()
        for r in rows:
            wr.writerow({c:(int(r[c]) if isinstance(r.get(c),bool) else round(r[c],4) if isinstance(r.get(c),float) else r.get(c,'')) for c in cols})
        return out.getvalue(),len(rows)

world=World()
agent=Learner()

def dispatch(raw):
    global world,agent
    req=json.loads(raw); op=req['op']
    if op=='reset':
        world=World(req.get('mode','practice'),req.get('seed',42),req.get('drain','1'),req.get('slip',True))
        if req.get('fresh'): agent=Learner(req.get('seed',42))
    elif op=='step': world.step(req['action'],req.get('dt',0),record=False)
    elif op=='clock': world.step(None,req.get('dt',0),record=False)
    elif op=='auto': agent.advance(world,req.get('learn',True)) if world.t<100 else None
    elif op=='train':
        mode,drain=world.mode,world.drain_opt
        for _ in range(min(50,int(req.get('count',10)))):
            w=World(mode,agent.rng.randrange(2**31),drain,world.slip)
            while w.t<100: agent.advance(w)
        world=World(mode,agent.rng.randrange(2**31),drain,world.slip)
    elif op=='state': pass
    elif op=='csv':
        text,n=agent.csv(req.get('kind','telemetry'))
        return json.dumps(dict(csv=text,rows=n))
    elif op=='export':
        return json.dumps(dict(state=world.state(),log=world.log,training=agent.history,evaluation=agent.eval_history,q=[dict(state=list(k),values=v) for k,v in agent.q.items()],parameters=dict(gamma=.95,learning_rate=.15,epsilon=agent.epsilon,drain_option=world.drain_opt,slip=world.slip,agent_dt_seconds=.2)))
    return json.dumps(dict(state=world.state(),agent=dict(episodes=agent.episodes,epsilon=agent.epsilon,states=len(agent.q),explorations=agent.explorations,exploitations=agent.exploitations,history=agent.history[-200:],telemetry_rows=len(agent.telemetry),evaluations=len(agent.eval_history))))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--episodes',type=int,default=1000);p.add_argument('--mode',choices=['practice','extended'],default='practice');p.add_argument('--drain',choices=DRAIN_OPTIONS,default='1');p.add_argument('--output',default='training.json')
    p.add_argument('--telemetry-csv');p.add_argument('--balance-csv');args=p.parse_args()
    for i in range(args.episodes):
        w=World(args.mode,i,args.drain)
        while w.t<100: agent.advance(w)
    if args.episodes > 0: world=w
    with open(args.output,'w',encoding='utf-8') as f: f.write(dispatch('{"op":"export"}'))
    for path,kind in [(args.telemetry_csv,'telemetry'),(args.balance_csv,'balance')]:
        if path:
            with open(path,'w',encoding='utf-8',newline='') as f: f.write(agent.csv(kind)[0])
    print(f'{agent.episodes} episodios; resultados en {args.output}')
