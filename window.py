import numpy as np
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QLabel, QDoubleSpinBox, QSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QHeaderView, QSizePolicy, QProgressBar,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from constants import SOLUTION_KEYS, SOLUTION_LABELS, SOLUTION_COLORS, SOLUTION_DEFAULTS
from worker import SimulationWorker
from styles import APP_STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Горячий кофе — Монте-Карло')
        self.setMinimumSize(1280, 720)
        self._worker: SimulationWorker | None = None
        self._build_ui()
        self.setStyleSheet(APP_STYLESHEET)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        root.addWidget(self._build_left_panel())
        root.addWidget(self._build_separator())
        root.addWidget(self._build_right_panel(), stretch=1)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(290)
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl_title = QLabel('Горячий кофе')
        lbl_title.setObjectName('title')
        lbl_sub = QLabel('Симуляция методом Монте-Карло')
        lbl_sub.setObjectName('subtitle')
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)

        layout.addWidget(self._build_model_group())
        layout.addWidget(self._build_solutions_group())
        layout.addWidget(self._build_run_section())
        layout.addStretch()
        return panel

    def _build_model_group(self) -> QGroupBox:
        group = QGroupBox('Параметры модели')
        grid  = QGridLayout(group)
        grid.setSpacing(7)
        grid.setColumnStretch(1, 1)

        self.spin_n          = self._int_spin(1_000, 1_000_000, 100_000, 10_000)
        self.spin_clients    = self._int_spin(1_000, 10_000_000, 365_000, 1_000)
        self.spin_p_burn     = self._float_spin(0.0, 1.0, 0.70, 0.01)
        self.spin_p_severe   = self._float_spin(0.0, 1.0, 0.15, 0.01)
        self.spin_minor_min  = self._int_spin(0, 100_000,   50, 10)
        self.spin_minor_max  = self._int_spin(0, 100_000,  300, 10)
        self.spin_severe_min = self._int_spin(0, 100_000,  500, 50)
        self.spin_severe_max = self._int_spin(0, 100_000, 3000, 100)

        rows = [
            ('Итераций (N):',         self.spin_n),
            ('Клиентов в год:',       self.spin_clients),
            ('P(ожог | разлив):',     self.spin_p_burn),
            ('P(тяжёлый | ожог):',    self.spin_p_severe),
            ('Ущерб лёгкий, мин:',   self.spin_minor_min),
            ('Ущерб лёгкий, макс:',  self.spin_minor_max),
            ('Ущерб тяжёлый, мин:',  self.spin_severe_min),
            ('Ущерб тяжёлый, макс:', self.spin_severe_max),
        ]
        for i, (lbl, widget) in enumerate(rows):
            grid.addWidget(QLabel(lbl), i, 0)
            grid.addWidget(widget, i, 1)
        return group

    def _build_solutions_group(self) -> QGroupBox:
        group = QGroupBox('Решения')
        grid  = QGridLayout(group)
        grid.setSpacing(7)

        for col, txt in enumerate(['', 'P(разлив)', 'Затраты, т.р.']):
            h = QLabel(txt)
            h.setObjectName('colHeader')
            grid.addWidget(h, 0, col)

        self.solution_spins: dict[str, tuple[QDoubleSpinBox, QSpinBox]] = {}
        for row, (key, label, (p_sp, cost)) in enumerate(
                zip(SOLUTION_KEYS, SOLUTION_LABELS, SOLUTION_DEFAULTS), start=1):
            dot = QLabel('●')
            dot.setObjectName(f'dot{key}')
            dot.setFixedWidth(20)
            name_lbl = QLabel(label)
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)
            row_layout.addWidget(dot)
            row_layout.addWidget(name_lbl)
            grid.addWidget(row_widget, row, 0)

            sp_p = self._float_spin(0.0, 1.0, p_sp, 0.001, decimals=3)
            sp_c = self._int_spin(0, 100_000, cost, 100)
            grid.addWidget(sp_p, row, 1)
            grid.addWidget(sp_c, row, 2)
            self.solution_spins[key] = (sp_p, sp_c)
        return group

    def _build_run_section(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.btn_run = QPushButton('▶   Запустить симуляцию')
        self.btn_run.setObjectName('runBtn')
        self.btn_run.clicked.connect(self._run_simulation)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setObjectName('progress')
        self.progress.setVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)

        self.status_label = QLabel('Готов к запуску')
        self.status_label.setObjectName('status')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.btn_run)
        layout.addWidget(self.progress)
        layout.addWidget(self.status_label)
        return w

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        lbl_stats = QLabel('Статистика по решениям')
        lbl_stats.setObjectName('sectionTitle')
        layout.addWidget(lbl_stats)

        self.table = QTableWidget(3, 5)
        self.table.setHorizontalHeaderLabels(
            ['Решение', 'Среднее, т.р.', 'Ст. откл.', 'P95', 'P99'])
        self.table.verticalHeader().setVisible(False)
        self.table.setMaximumHeight(120)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setObjectName('statsTable')
        layout.addWidget(self.table)

        for row, label in enumerate(SOLUTION_LABELS):
            self.table.setItem(row, 0, self._centered_item(label))
            for col in range(1, 5):
                self.table.setItem(row, col, self._centered_item('—'))

        lbl_chart = QLabel('Распределение годовых затрат')
        lbl_chart.setObjectName('sectionTitle')
        layout.addWidget(lbl_chart)

        self.figure = Figure(facecolor='#F8F9FA')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.canvas)

        self._draw_empty_chart()
        return panel

    def _int_spin(self, mn, mx, val, step) -> QSpinBox:
        s = QSpinBox()
        s.setRange(mn, mx)
        s.setValue(val)
        s.setSingleStep(step)
        return s

    def _float_spin(self, mn, mx, val, step, decimals=2) -> QDoubleSpinBox:
        s = QDoubleSpinBox()
        s.setDecimals(decimals)
        s.setRange(mn, mx)
        s.setValue(val)
        s.setSingleStep(step)
        return s

    def _build_separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setObjectName('separator')
        return sep

    @staticmethod
    def _centered_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _collect_params(self) -> dict:
        solutions = {
            key: (sp_p.value(), float(sp_c.value()))
            for key, (sp_p, sp_c) in self.solution_spins.items()
        }
        return {
            'n':          self.spin_n.value(),
            'clients':    self.spin_clients.value(),
            'p_burn':     self.spin_p_burn.value(),
            'p_severe':   self.spin_p_severe.value(),
            'dmg_minor':  (self.spin_minor_min.value(), self.spin_minor_max.value()),
            'dmg_severe': (self.spin_severe_min.value(), self.spin_severe_max.value()),
            'solutions':  solutions,
        }

    def _run_simulation(self):
        if self._worker and self._worker.isRunning():
            return
        self.btn_run.setEnabled(False)
        self.btn_run.setText('⏳   Симуляция...')
        self.progress.setVisible(True)
        self.status_label.setText('Выполняется...')

        self.progress.setRange(0, self.spin_n.value() * len(SOLUTION_KEYS))
        self.progress.setValue(0)
        self._worker = SimulationWorker(self._collect_params())
        self._worker.progress.connect(self.progress.setValue)
        self._worker.finished.connect(self._on_results)
        self._worker.start()

    def _on_results(self, results: dict):
        self.btn_run.setEnabled(True)
        self.btn_run.setText('▶   Запустить симуляцию')
        self.progress.setVisible(False)
        self.status_label.setText('Симуляция завершена')

        for row, key in enumerate(SOLUTION_KEYS):
            res = results[key]
            values = [
                SOLUTION_LABELS[row],
                f'{np.mean(res):.0f}',
                f'{np.std(res):.0f}',
                f'{np.percentile(res, 95):.0f}',
                f'{np.percentile(res, 99):.0f}',
            ]
            for col, val in enumerate(values):
                item = self._centered_item(val)
                if col == 0:
                    item.setForeground(QColor(SOLUTION_COLORS[row]))
                self.table.setItem(row, col, item)

        self.figure.clear()
        axes = self.figure.subplots(1, 3)
        self.figure.patch.set_facecolor('#F8F9FA')

        for ax, key, color, label in zip(axes, SOLUTION_KEYS, SOLUTION_COLORS, SOLUTION_LABELS):
            res = results[key]
            clip_max = np.percentile(res, 98)
            data = res[res <= clip_max]

            ax.hist(data, bins=60, color=color, alpha=0.82, edgecolor='none', zorder=2)
            mean_val = np.mean(res)
            p95      = np.percentile(res, 95)

            ax.axvline(mean_val, color='#2C3E50', linestyle='--', linewidth=1.5, zorder=3,
                       label=f'Среднее: {mean_val:.0f}')
            ax.axvline(p95, color='#6C757D', linestyle=':', linewidth=1.2, zorder=3,
                       label=f'P95: {p95:.0f}')

            ax.set_title(label, fontsize=10, fontweight='bold', pad=8, color='#212529')
            ax.set_xlabel('Затраты, тыс. руб.', fontsize=8, color='#495057')
            ax.set_ylabel('Частота' if ax is axes[0] else '', fontsize=8, color='#495057')
            ax.tick_params(labelsize=7, colors='#495057')
            ax.legend(fontsize=7, framealpha=0.9)
            ax.set_facecolor('#FFFFFF')
            for spine in ax.spines.values():
                spine.set_edgecolor('#DEE2E6')
                spine.set_linewidth(0.8)
            ax.grid(axis='y', color='#E9ECEF', linewidth=0.6, zorder=1)

        self.figure.tight_layout(pad=2.5)
        self.canvas.draw()

    def _draw_empty_chart(self):
        self.figure.clear()
        axes = self.figure.subplots(1, 3)
        self.figure.patch.set_facecolor('#F8F9FA')
        for ax, label, color in zip(axes, SOLUTION_LABELS, SOLUTION_COLORS):
            ax.set_facecolor('#FFFFFF')
            ax.set_title(label, fontsize=10, fontweight='bold', color='#212529')
            ax.set_xlabel('Затраты, тыс. руб.', fontsize=8, color='#495057')
            ax.text(0.5, 0.5, 'Нет данных', transform=ax.transAxes,
                    ha='center', va='center', fontsize=11, color='#ADB5BD')
            for spine in ax.spines.values():
                spine.set_edgecolor('#DEE2E6')
        self.figure.tight_layout(pad=2.5)
        self.canvas.draw()
