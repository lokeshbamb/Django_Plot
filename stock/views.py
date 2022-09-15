from django.shortcuts import render
from django.http import HttpResponse
import datetime
import pandas as pd

#from mpl_finance import candlestick_ohlc
import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
from matplotlib.widgets import Cursor

import mpld3
from mpld3 import plugins

# Create your views here.

# Define some CSS to control our custom labels
css = """
table
{
  border-collapse: collapse;
}
th
{
  color: #ffffff;
  background-color: #000000;
}
td
{
  background-color: #cccccc;
}
table, th, td
{
  font-family:Arial, Helvetica, sans-serif;
  border: 1px solid black;
  text-align: right;
}
"""


def home(request):
    now = datetime.datetime.now()
    m = now.strftime("%m")
    y = now.strftime("%Y")
    d = now.strftime("%d")
    s = str(y) + '-' + str(m) + '-' + str(d)
    return render(request, 'home.html', {'out':"Let's Start", 'today':s})
    
def plot(request):

    now = datetime.datetime.now()
    m = now.strftime("%m")
    y = now.strftime("%Y")
    d = now.strftime("%d")
    s = str(y) + '-' + str(m) + '-' + str(d)
    
    c = request.POST['MyList']     #company name
    sd = request.POST['start_date']
    ed = request.POST['end_date']
    comp = pd.read_csv('/home/lokesh/ML/djangos/charting/stock/NIFTY-200/' + c + '.csv',index_col=0,parse_dates=True,infer_datetime_format=True)
    comp = comp[(comp.index > sd) & (comp.index <= ed)]
    print(comp)
    company = comp.to_html()
    
    fig, ax = plt.subplots(figsize=(15.92,6.5))
    plt.subplots_adjust(left = 0.04, right = 0.98)
    #plt.rcParams["figure.figsize"] = (40,10)
    ax.plot(comp.index, comp['CLOSE'])
    #candlestick_ohlc(ax, zip(mdates.date2num(comp.index.to_pydatetime()), comp['OPEN'], comp['HIGH'], comp['LOW'], comp['CLOSE']),width=0.5,colorup='g',colordown='r')
    ax.set_xlabel('Dates')
    ax.set_ylabel('Closing Price')
    ax.grid(alpha=0.2)
    #ax.set_title('HTML tooltips', size=20)
    #cursor = Cursor(ax, useblit=True, color='blue', linewidth=2)
    plugins.clear(fig)
    plugins.connect(fig, plugins.Reset(), plugins.BoxZoom(), plugins.Zoom())
    mpld3.plugins.connect(fig, MousePositionDatePlugin())
    fig = plt.gcf()
    html_fig = mpld3.fig_to_html(fig,template_type='general')
    plt.close(fig)
    
    return render(request, "chart.html", {'active_page' : 'chart.html', 'div_figure' : html_fig, 'sd' : sd, 'ed' : ed, 'cn' : c, 'today' : s})
    
class MousePositionDatePlugin(mpld3.plugins.PluginBase):
    """Plugin for displaying mouse position with a datetime x axis."""

    JAVASCRIPT = """
    mpld3.register_plugin("mousepositiondate", MousePositionDatePlugin);
    MousePositionDatePlugin.prototype = Object.create(mpld3.Plugin.prototype);
    MousePositionDatePlugin.prototype.constructor = MousePositionDatePlugin;
    MousePositionDatePlugin.prototype.requiredProps = [];
    MousePositionDatePlugin.prototype.defaultProps = {
    fontsize: 12,
    xfmt: "%d-%b-%y",
    yfmt: ".3g"
    };
    function MousePositionDatePlugin(fig, props) {
    mpld3.Plugin.call(this, fig, props);
    }
    MousePositionDatePlugin.prototype.draw = function() {
    var fig = this.fig;
    var xfmt = d3.timeFormat(this.props.xfmt);
    var yfmt = d3.format(this.props.yfmt);
    var coords = fig.canvas.append("text").attr("class", "mpld3-coordinates").style("text-anchor", "end").style("font-size", this.props.fontsize).attr("x", this.fig.width - 5).attr("y", this.fig.height - 5);
    for (var i = 0; i < this.fig.axes.length; i++) {
      var update_coords = function() {
        var ax = fig.axes[i];
        return function() {
          var pos = d3.mouse(this);
          x = ax.xdom.invert(pos[0]);
          y = ax.ydom.invert(pos[1]);
          coords.text(" " + xfmt(x) + ", " + yfmt(y) + " ");
        };
      }();
      fig.axes[i].baseaxes.on("mousemove", update_coords).on("mouseout", function() {
        coords.text("");
      });
    }
    };
    """
    def __init__(self, fontsize=14, xfmt="%d-%b-%y", yfmt=".3g"):
        self.dict_ = {"type": "mousepositiondate",
                      "fontsize": fontsize,
                      "xfmt": xfmt,
                      "yfmt": yfmt}
                      
class CrosshairCursorPlugin(mpld3.plugins.PluginBase):
    """Plugin for displaying crosshair cursor with a datetime x axis."""

    JAVASCRIPT = """
    mpld3.register_plugin("crosshaircursor", CrosshairCursorPlugin);
    CrosshairCursorPlugin.prototype = Object.create(mpld3.Plugin.prototype);
    CrosshairCursorPlugin.prototype.constructor = CrosshairCursorPlugin;
    CrosshairCursorPlugin.prototype.requiredProps = [];
    CrosshairCursorPlugin.prototype.defaultProps = {
    xfmt: "%d-%b-%y",
    yfmt: ".3g"
    };
    function CrosshairCursorPlugin(fig, props) {
    mpld3.Plugin.call(this, fig, props);
    }
    CrosshairCursorPlugin.prototype.draw = function() {
    var fig = this.fig;
    var xfmt = d3.timeFormat(this.props.xfmt);
    var yfmt = d3.format(this.props.yfmt);
    var coords = fig.canvas.append("text").attr("class", "mpld3-coordinates").style("text-anchor", "end").style("font-size", this.props.fontsize).attr("x", this.fig.width - 5).attr("y", this.fig.height - 5);
    for (var i = 0; i < this.fig.axes.length; i++) {
      var update_coords = function() {
        var ax = fig.axes[i];
        return function() {
          var pos = d3.mouse(this);
          x = ax.xdom.invert(pos[0]);
          y = ax.ydom.invert(pos[1]);
          coords.text(" " + xfmt(x) + ", " + yfmt(y) + " ");
          ax.axvline(x = xfmt(x), color = "red", alpha = 0.2)
          ax.axhline(y = yfmt(y), color = "red", alpha = 0.2)
        };
      }();
      fig.axes[i].baseaxes.on("mousemove", update_coords).on("mouseout", function() {
        coords.text("");
      });
    }
    };
    """
    def __init__(self, fontsize=14, xfmt="%d-%b-%y", yfmt=".3g"):
        self.dict_ = {"type": "mousepositiondate",
                      "fontsize": fontsize,
                      "xfmt": xfmt,
                      "yfmt": yfmt}
