
from flask import Blueprint
from core.processing.file.load_json import LoadJson

ajax_reports = Blueprint('load_reports', __name__, template_folder='templates')


@ajax_reports.route('/load_reports', methods=['GET', 'POST'])
def load_reports():
    json_reports = LoadJson()
    return json_reports.load_json_list()
