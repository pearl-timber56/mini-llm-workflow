from dataclasses import dataclass, field
from typing import Callable, Dict, List

@dataclass
class Step:
    name: str
    fn: Callable
    needs: List[str] = field(default_factory=list)

class Workflow:
    def __init__(self):
        self.steps: Dict[str, Step] = {}

    def add(self, name, fn, needs=None):
        self.steps[name] = Step(name, fn, needs or [])
        return self

    def _order(self):
        done, result = set(), []
        while len(result) < len(self.steps):
            ready = [s for n, s in self.steps.items() if n not in done and all(d in done for d in s.needs)]
            if not ready:
                raise ValueError('Cycle or missing dependency')
            for s in ready:
                result.append(s.name)
                done.add(s.name)
        return result

    def run(self, context=None):
        ctx = context or {}
        for name in self._order():
            ctx[name] = self.steps[name].fn(ctx)
        return ctx

def mock_llm(prompt):
    words = [w.strip('.,!?') for w in prompt.lower().split() if len(w) > 4]
    return {'summary': prompt[:80], 'keywords': sorted(set(words))[:5]}

wf = Workflow()
wf.add('ingest', lambda ctx: 'AI agents automate LLM workflows with tools and memory.')
wf.add('llm', lambda ctx: mock_llm(ctx['ingest']), needs=['ingest'])
wf.add('report', lambda ctx: 'Summary: ' + ctx['llm']['summary'] + ' | Keywords: ' + ', '.join(ctx['llm']['keywords']), needs=['llm'])
result = wf.run()
print(result['report'])