"""Can Finder 5000: entorno independiente de la interfaz, Python estándar."""
import random
import math
import json

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
NAMES = ['Norte', 'Este', 'Sur', 'Oeste', 'Esperar', 'Recargar']
VALUES = [1., 2., 4.]

class World:
    def __init__(self, mode='practice', seed=42):
        self.mode, self.seed = mode, int(seed)
        self.rng = random.Random(self.seed)
        self.x = self.y = self.t = self.caught = self.rescues = 0
        self.energy = 100.
        self.score = self.discounted = self.elapsed = 0.
        self.cans = {}
        self.log = []
        self.last = dict(message='Listo en la estación. Batería al 100%.', drain=0., angle=0., reward=0., rescue=False)
        for _ in range(12): self.spawn()

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

    def step(self, action, dt=1.):
        if self.t >= 100 or action not in self.actions(): return False
        x0, y0, e0 = self.x, self.y, self.energy
        dt = 1. if self.mode == 'practice' else max(0., float(dt))
        self.elapsed += dt
        drain = angle = 0.
        reward = 0.
        message = NAMES[action]
        if action < 4:
            drain = max(0., self.rng.gauss(10 if e0 > 40 else 16, 4 if e0 > 40 else 6))
            angle = self.rng.gauss(0,25)
            direction = (action + (1 if angle > 30 else -1 if angle < -30 else 0)) % 4
            dx, dy = DIRS[direction]
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < 10 and 0 <= ny < 10: self.x, self.y = nx, ny
            else: message += ' · Colisión con el borde'
            if abs(angle)>30: message += ' · ¡Patinó a la '+('derecha!' if angle>0 else 'izquierda!')
            reward = -.05
        elif action == 4:
            reward = .1 if self.mode == 'practice' else 0.
            message = 'Esperar · '+ ('+0.10 sin consumo' if self.mode=='practice' else 'reloj activo')
        # Extended: 0.5 percentage points/second, also when waiting; charging is instant.
        if self.mode == 'extended': drain += .5 * dt
        self.energy -= drain
        rescue = self.energy <= 0
        if rescue:
            self.x = self.y = 0
            self.energy = 100.
            self.rescues += 1
            reward = -3.
            message = 'BATERÍA AGOTADA · Rescate −3.00 · Regreso a la base'
        elif action == 5:
            self.energy = 100.
            message = 'Recarga completa · 100%'
        elif action < 4 and (self.x,self.y) in self.cans:
            color = self.cans.pop((self.x,self.y))
            reward = 1. if self.mode=='practice' else VALUES[color]
            self.caught += 1
            self.spawn()
            message += ' · Lata +'+str(reward)
        if self.mode=='extended' and len(self.cans)<20 and self.rng.random() < 1-math.exp(-dt/8): self.spawn()
        self.score += reward
        self.discounted += .95**self.t * reward
        self.t += 1
        self.last = dict(message=message, drain=drain, angle=angle, reward=reward, rescue=rescue, old=[x0,y0])
        self.log.append(dict(turn=self.t, action=NAMES[action], x0=x0,y0=y0,energy0=e0,x=self.x,y=self.y,energy=self.energy,drain=drain,angle=angle,reward=reward,score=self.score,discounted=self.discounted,rescue=rescue,dt=dt))
        return True

    def state(self):
        e=self.energy
        phi=lambda z: .5*(1+math.erf(z/math.sqrt(2)))
        return dict(mode=self.mode,seed=self.seed,x=self.x,y=self.y,t=self.t,energy=e,high=e>40,score=self.score,discounted=self.discounted,caught=self.caught,rescues=self.rescues,cans=[[x,y,c] for (x,y),c in self.cans.items()],last=self.last,elapsed=self.elapsed,alpha=phi((e-40-10)/4) if e>40 else None,beta=phi((e-16)/6) if e<=40 else None,done=self.t>=100)

class Learner:
    """Q-learning tabular con agregación de estado explícita; Q inicial cero."""
    def __init__(self, seed=42):
        self.rng=random.Random(seed)
        self.q={}
        self.episodes=0
        self.history=[]
        self.explorations=self.exploitations=0

    @property
    def epsilon(self): return max(.05, .995**self.episodes)

    def key(self,w):
        target=min(w.cans, key=lambda p:(abs(p[0]-w.x)+abs(p[1]-w.y),p))
        return (w.x,w.y,min(9,int(w.energy//10)),target[0]-w.x,target[1]-w.y,w.cans[target],(99-w.t)//10)

    def row(self,key): return self.q.setdefault(key,[0.]*6)

    def choose(self,w,explore=True):
        actions=w.actions()
        if explore and self.rng.random()<self.epsilon:
            self.explorations+=1
            return self.rng.choice(actions)
        if explore: self.exploitations+=1
        row=self.row(self.key(w)) if explore else self.q.get(self.key(w),[0.]*6); best=max(row[a] for a in actions)
        return self.rng.choice([a for a in actions if row[a]==best])

    def advance(self,w,learn=True):
        key=self.key(w); a=self.choose(w,learn)
        w.step(a,1.)
        if learn:
            target=w.last['reward']
            if not w.state()['done']: target+=.95*max(self.row(self.key(w))[b] for b in w.actions())
            row=self.row(key); row[a]+=.15*(target-row[a])
        if w.t==100 and learn:
            self.episodes+=1
            self.history.append(dict(episode=self.episodes,score=w.score,discounted=w.discounted,caught=w.caught,rescues=w.rescues))

world=World()
agent=Learner()

def dispatch(raw):
    global world,agent
    req=json.loads(raw); op=req['op']
    if op=='reset':
        world=World(req.get('mode','practice'),req.get('seed',42))
        if req.get('fresh'): agent=Learner(req.get('seed',42))
    elif op=='step': world.step(req['action'],req.get('dt',1))
    elif op=='auto': agent.advance(world,req.get('learn',True)) if world.t<100 else None
    elif op=='train':
        mode=world.mode
        for _ in range(min(50,int(req.get('count',10)))):
            w=World(mode,agent.rng.randrange(2**31))
            while w.t<100: agent.advance(w)
        world=World(mode,agent.rng.randrange(2**31))
    elif op=='export':
        return json.dumps(dict(state=world.state(),log=world.log,training=agent.history,q=[dict(state=list(k),values=v) for k,v in agent.q.items()],parameters=dict(gamma=.95,learning_rate=.15,epsilon=agent.epsilon)))
    return json.dumps(dict(state=world.state(),agent=dict(episodes=agent.episodes,epsilon=agent.epsilon,states=len(agent.q),explorations=agent.explorations,exploitations=agent.exploitations,history=agent.history[-200:])))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--episodes',type=int,default=1000);p.add_argument('--mode',choices=['practice','extended'],default='practice');p.add_argument('--output',default='training.json');args=p.parse_args()
    for i in range(args.episodes):
        w=World(args.mode,i)
        while w.t<100: agent.advance(w)
    if args.episodes > 0: world=w
    with open(args.output,'w',encoding='utf-8') as f: f.write(dispatch('{"op":"export"}'))
    print(f'{agent.episodes} episodios; resultados en {args.output}')
