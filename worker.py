import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal


class SimulationWorker(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int)

    def __init__(self, params: dict):
        super().__init__()
        self.p = params

    def run(self):
        results = {}
        n = self.p['n']
        chunk = max(1, n // 50)
        for sol_idx, (key, (p_spill, cost)) in enumerate(self.p['solutions'].items()):
            results[key] = self._simulate(p_spill, cost, sol_idx * n, chunk)
        self.finished.emit(results)

    def _simulate(self, p_spill: float, cost: float, offset: int, chunk: int) -> np.ndarray:
        p = self.p
        n        = p['n']
        clients  = p['clients']
        p_burn   = p['p_burn']
        p_severe = p['p_severe']
        d_minor  = p['dmg_minor']
        d_severe = p['dmg_severe']

        incidents  = np.random.binomial(clients, p_spill, n)
        total_loss = np.full(n, float(cost))
        for i in range(n):
            inc = incidents[i]
            if inc == 0:
                continue
            burns  = int((np.random.random(inc)   < p_burn).sum())
            if burns == 0:
                continue
            severe = int((np.random.random(burns) < p_severe).sum())
            minor  = burns - severe
            if severe:
                total_loss[i] += np.random.uniform(*d_severe, severe).sum()
            if minor:
                total_loss[i] += np.random.uniform(*d_minor,  minor).sum()
            if (i + 1) % chunk == 0:
                self.progress.emit(offset + i + 1)
        self.progress.emit(offset + n)
        return total_loss
