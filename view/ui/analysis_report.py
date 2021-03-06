
from flask import Blueprint, render_template, abort, request, Markup
from jinja2 import TemplateNotFound
from core.processing.file.load_json import LoadJson

analysis_report = Blueprint('analysis_report', __name__, template_folder='templates')


@analysis_report.route('/analysis_report', defaults={'page': 'index'})
@analysis_report.route('/analysis_report')
def show():
    try:
        sample_name = request.args.get('sample')
        json_object = LoadJson()
        json_content = json_object.load_json_content(sample_name)
        ui_javascript = ''
        if 'graph_data' in json_content:
            if 'javascript_code' in json_content['graph_data']:
                ui_javascript = Markup(json_content['graph_data']['javascript_code'])
        return render_template('pages/analysis_report.html', ui_data=None, json_content=json_content, ui_javascript=ui_javascript)
    except TemplateNotFound:
        abort(404)
