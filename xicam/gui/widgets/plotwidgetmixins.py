from qtpy.QtWidgets import QApplication
import pyqtgraph as pg
import numpy as np
from xicam.plugins import live_plugin


# TODO: refactor to support mixin pattern; conflict with plotwidget's attr magic


@live_plugin('PlotMixinPlugin')
class HoverHighlight(pg.PlotWidget):
    """
    Highlights any scatter spots moused-over, giving a feel that they can be clicked on for more info
    """

    def __init__(self, *args, **kwargs):
        super(HoverHighlight, self).__init__(*args, **kwargs)
        self._last_highlighted = None
        self._last_pen = None

    def mouseMoveEvent(self, ev):
        if self._last_highlighted:
            self._last_highlighted.setPen(self._last_pen)
            self._last_highlighted = None

        super(HoverHighlight, self).mouseMoveEvent(ev)

        if self.plotItem.boundingRect().contains(ev.pos()):
            mousePoint = self.plotItem.mapToView(pg.Point(ev.pos()))

            for item in self.scene().items():
                if isinstance(item, pg.PlotDataItem):
                    if item.curve.mouseShape().contains(mousePoint):
                        scatter = item.scatter  # type: pg.ScatterPlotItem
                        points = scatter.pointsAt(mousePoint)
                        if points:
                            self._last_pen = points[0].pen()
                            self._last_highlighted = points[0]
                            points[0].setPen(pg.mkPen("w", width=2))
                            break


@live_plugin('PlotMixinPlugin')
class ClickHighlight(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super(ClickHighlight, self).__init__(*args, **kwargs)
        self._last_highlighted = None
        self._last_item = None
        self._last_pen = None
        self._last_curve_pen = None

    def wireup_item(self, item):
        item.sigPointsClicked.connect(self.highlight)
        return item

    def highlight(self, item, points):
        if self._last_item:
            self._last_item.setPen(self._last_curve_pen)
            # self._last_item.setZValue(0)
            self._last_item = None

        self._last_item = item
        self._last_curve_pen = item.opts['pen']
        item.setPen(pg.mkPen('w', width=6))
        # item.setZValue(100)


@live_plugin('PlotMixinPlugin')
class CurveLabels(HoverHighlight, ClickHighlight):
    def __init__(self, *args, **kwargs):
        super(CurveLabels, self).__init__(*args, **kwargs)

        self._arrow = None
        self._text = None
        self._curvepoint = None

    def plot(self, *args, **kwargs):
        if "symbolSize" not in kwargs:
            kwargs["symbolSize"] = 10
        if "symbol" not in kwargs:
            kwargs["symbol"] = "o"
        if "symbolPen" not in kwargs:
            kwargs["symbolPen"] = pg.mkPen((0, 0, 0, 0))
        if "symbolBrush" not in kwargs:
            kwargs["symbolBrush"] = pg.mkBrush((0, 0, 0, 0))

        item = self.plotItem.plot(*args, **kwargs)
        # Note: this is sensitive to order of connections; ClickHighlight seems to regenerate all spots, breaking showLabel unless done in this order
        item.sigPointsClicked.connect(self.showLabel)
        self.wireup_item(item)

        return item

    def showLabel(self, item, points):
        if self._curvepoint:
            self.scene().removeItem(self._arrow)
            self.scene().removeItem(self._text)

        point = points[0]
        self._curvepoint = pg.CurvePoint(item.curve)
        self.addItem(self._curvepoint)
        self._arrow = pg.ArrowItem(angle=90)
        self._arrow.setParentItem(self._curvepoint)
        self._arrow.setZValue(10000)
        self._text = pg.TextItem(f'{item.name()}\nx: {point._data["x"]}\ny: {point._data["y"]}', anchor=(0.5, -.5), border=pg.mkPen("w"), fill=pg.mkBrush("k"))
        self._text.setZValue(10000)
        self._text.setParentItem(self._curvepoint)

        self._curvepoint.setIndex(list(item.scatter.points()).index(point))


if __name__ == "__main__":
    qapp = QApplication([])
    w = CurveLabels()
    for i in range(10):
        pen = pg.mkColor((i, 10))
        w.plot(np.random.random((100,)) + i * 0.5, name=str(i), pen=pen)

    w.show()

    qapp.exec_()
