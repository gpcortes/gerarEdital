from caworker import Worker
import time
import json
from urllib.parse import quote
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import text
import pandas as pd
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import json
import envconfiguration as config
import subprocess
import re
import os
import sys
import locale
from unidecode import unidecode

def convert_to(source, folder, timeout=None):
    args = [
        libreoffice_exec(), '--headless', '--convert-to', 'pdf', source,
        '--outdir', folder
    ]

    process = subprocess.run(args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             timeout=timeout)
    filename = re.search('-> (.*?) using filter', process.stdout.decode())

    if filename is None:
        raise LibreOfficeError(process.stdout.decode())
    else:
        return os.path.basename(filename.group(1))


def libreoffice_exec():
    # TODO Provide support for more platforms
    if sys.platform == 'darwin':
        return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    elif sys.platform == 'linux':
        return 'soffice'
    else:
        return 'libreoffice'


class LibreOfficeError(Exception):

    def __init__(self, output):
        self.output = output


def unique(list1):

    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    # print list
    return unique_list


def get_engine(rede):
    database = ''
    if rede  == 'efg':
        database = config.EFG_DOMAINS_DB  # type: ignore
    elif rede == 'cotec':
        database = config.COTEC_DOMAINS_DB  # type: ignore
    string_connection = "mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(
        user=config.CAMUNDA_DOMAINS_USER,  # type: ignore
        password=quote(config.CAMUNDA_DOMAINS_PASS),  # type: ignore
        host=config.CAMUNDA_DOMAINS_HOST,  # type: ignore
        port=config.CAMUNDA_DOMAINS_PORT,  # type: ignore
        database=database  # type: ignore
    )
    print(string_connection)
    return create_engine(string_connection)


def criaredital(rede):

    turmas_planejadas = pd.read_sql_query("""
        SELECT
        tpo.*, esc.escola, um.municipio, esc.email, esc.telefone, md.modalidade, tc.tipo, cr.curso, ee.id AS 'num_edital_id', ee.dt_ini_edit, ee.dt_fim_edit, ee.dt_ini_insc, ee.dt_fim_insc, ee.num_edital
        from Turmas_planejado_orcado tpo 
        inner JOIN escolas esc ON esc.id = tpo.escola_id
        left JOIN udepi_municipio um ON um.escola_id = esc.id
        INNER JOIN modalidade md ON md.id = tpo.modalidade_id
        INNER JOIN tipo_curso tc ON tc.id = tpo.tipo_curso_id
        INNER JOIN cursos cr ON cr.id = tpo.curso_id
        INNER JOIN edital_ensino ee ON ee.id = tpo.num_edital_id
        WHERE ee.`status`='0'AND ee.dt_ini_edit and ee.dt_fim_edit AND ee.dt_ini_insc AND ee.dt_fim_insc is NOT null
    """, con=get_engine(rede))
    #turmas_planejadas = turmas_planejadas[turmas_planejadas['id']==id_]
    # turmas_planejadas.values[0]
    #turmas_planejadas['previsao_abertura_edital'] = datetime.strftime(pd.Timestamp(turmas_planejadas['previsao_abertura_edital'].values[0]),'%Y-%m-%d')
    #turmas_planejadas = turmas_planejadas_edital['num_edital_id'].groupby(by='num_edital_id')

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    default_date = datetime.strftime(datetime(1900, 1, 1), '%d/%m/%Y')

    turmas_planejadas['previsao_abertura_edital_estenso'] = datetime.strftime(
        pd.Timestamp(
            turmas_planejadas['dt_ini_edit'].values[0]),  # type: ignore
        '%d de %B de %Y') if turmas_planejadas['dt_ini_edit'].values[
            0] is not None else default_date
    turmas_planejadas[
        'previsao_fechamento_edital_estenso'] = datetime.strftime(
            pd.Timestamp(
                turmas_planejadas['dt_fim_edit'].values[0]),  # type: ignore
            '%d de %B de %Y') if turmas_planejadas['dt_ini_edit'].values[
                0] is not None else default_date
    turmas_planejadas['previsao_abertura_edital_normal'] = datetime.strftime(
        pd.Timestamp(
            turmas_planejadas['dt_ini_edit'].values[0]),  # type: ignore
        '%d/%m/%Y') if turmas_planejadas['dt_ini_edit'].values[
            0] is not None else default_date
    turmas_planejadas['previsao_fechamento_edital_normal'] = datetime.strftime(
        pd.Timestamp(
            turmas_planejadas['dt_fim_edit'].values[0]),  # type: ignore
        '%d/%m/%Y') if turmas_planejadas['dt_ini_edit'].values[
            0] is not None else default_date
    turmas_planejadas['previsao_inicio_inscricao'] = datetime.strftime(
        pd.Timestamp(
            turmas_planejadas['dt_ini_insc'].values[0]),  # type: ignore
        '%d/%m/%Y') if turmas_planejadas['dt_ini_edit'].values[
            0] is not None else default_date
    turmas_planejadas['previsao_fim_inscricao'] = datetime.strftime(
        pd.Timestamp(
            turmas_planejadas['dt_fim_insc'].values[0]),  # type: ignore
        '%d/%m/%Y') if turmas_planejadas['dt_ini_edit'].values[
            0] is not None else default_date
    turmas_planejadas['data_inicio_curso'] = datetime.strftime(
        pd.Timestamp(
            turmas_planejadas['previsao_inicio'].values[0]),  # type: ignore
        '%d de %B de %Y') if turmas_planejadas['previsao_inicio'].values[
            0] is not None else default_date

    turmas_planejadas[
        'data_resultado'] = turmas_planejadas['dt_fim_insc'] + timedelta(
            days=7)  # type: ignore
    turmas_planejadas['dt_resultado'] = datetime.strftime(
        pd.Timestamp(
            turmas_planejadas['data_resultado'].values[0]),  # type: ignore
        '%d de %B de %Y') if turmas_planejadas['data_resultado'].values[
            0] is not None else default_date

    turmas_planejadas[
        'data_resultado_final'] = turmas_planejadas['dt_fim_insc'] + timedelta(
            days=7)  # type: ignore

    turmas_planejadas[
        'data_recurso_edital'] = turmas_planejadas['dt_ini_insc'] + timedelta(
            days=-2)  # type: ignore

    turmas_planejadas['data_resultado_final'] = datetime.strftime(
        pd.Timestamp(
            turmas_planejadas['data_resultado_final'].values[0]),  # type: ignore
        '%d de %B de %Y') if turmas_planejadas['data_resultado_final'].values[
            0] is not None else default_date

    content = turmas_planejadas.to_dict('records')

    result_json = turmas_planejadas.to_json(orient="index")

    parsed_json = json.loads(result_json)

    print(json.dumps(parsed_json, indent=4))

    # content = json.loads(turmas_planejadas.to_json(orient='values'))
    # columns = [{
    #     "name": "id",
    #     "type": "integer"
    # }, {
    #     "name": "diretoria",
    #     "type": "string"
    # }, {
    #     "name": "escola_id",
    #     "type": "integer"
    # }, {
    #     "name": "tipo_curso_id",
    #     "type": "integer"
    # }, {
    #     "name": "curso_id",
    #     "type": "string"
    # }, {
    #     "name": "turno",
    #     "type": "string"
    # }, {
    #     "name": "ano",
    #     "type": "integer"
    # }, {
    #     "name": "modalidade_id",
    #     "type": "integer"
    # }, {
    #     "name": "trimestre",
    #     "type": "integer"
    # }, {
    #     "name": "carga_horaria",
    #     "type": "integer"
    # }, {
    #     "name": "vagas_totais",
    #     "type": "integer"
    # }, {
    #     "name": "vagas_turma",
    #     "type": "integer"
    # }, {
    #     "name": "carga_horaria_total",
    #     "type": "integer"
    # }, {
    #     "name": "previsao_inicio",
    #     "type": "string"
    # }, {
    #     "name": "previsao_fim",
    #     "type": "string"
    # }, {
    #     "name": "dias_semana",
    #     "type": "string"
    # }, {
    #     "name": "previsao_abertura_edital",
    #     "type": "string"
    # }, {
    #     "name": "previsao_fechamento_edital",
    #     "type": "string"
    # }, {
    #     "name": "data_registro",
    #     "type": "string"
    # }, {
    #     "name": "eixo_id",
    #     "type": "integer"
    # }, {
    #     "name": "udepi_id",
    #     "type": "integer"
    # }, {
    #     "name": "situacao",
    #     "type": "integer"
    # }, {
    #     "name": "jus_reprovacao",
    #     "type": "string"
    # }, {
    #     "name": "num_edital_id",
    #     "type": "integer"
    # }, {
    #     "name": "escola",
    #     "type": "string"
    # }, {
    #     "name": "municipio",
    #     "type": "string"
    # }, {
    #     "name": "email",
    #     "type": "string"
    # }, {
    #     "name": "telefone",
    #     "type": "string"
    # }, {
    #     "name": "modalidade",
    #     "type": "string"
    # }, {
    #     "name": "tipo",
    #     "type": "string"
    # }, {
    #     "name": "curso",
    #     "type": "string"
    # }, {
    #     "name": "num_edital",
    #     "type": "integer"
    # }, {
    #     "name": "dt_ini_edit",
    #     "type": "string"
    # }, {
    #     "name": "dt_fim_edit",
    #     "type": "string"
    # }, {
    #     "name": "dt_ini_insc",
    #     "type": "string"
    # }, {
    #     "name": "dt_fim_insc",
    #     "type": "string"
    # }, {
    #     "name": "previsao_abertura_edital_estenso",
    #     "type": "string"
    # }, {
    #     "name": "previsao_fechamento_edital_estenso",
    #     "type": "string"
    # }, {
    #     "name": "previsao_abertura_edital_normal",
    #     "type": "string"
    # }, {
    #     "name": "previsao_fechamento_edital_normal",
    #     "type": "string"
    # }, {
    #     "name": "previsao_inicio_inscricao",
    #     "type": "string"
    # }, {
    #     "name": "data_inicio_curso",
    #     "type": "string"
    # }]

    # mappedJson = []
    # # print(len(content[0]), len(columns))
    # for cont in range(len(content)):
    #     mappedObject = {}
    #     for col in range(len(columns)):
    #         mappedObject[columns[col]["name"]] = content[cont][col]
    #     mappedJson.append(mappedObject)

    # turmas_planejadas = mappedJson
    turmas_planejadas = content

    idsEdital = []
    for turma in turmas_planejadas:
        idsEdital.append(turma["num_edital_id"])

    idsEdital = unique(idsEdital)
    resposta = {}

    for id in idsEdital:
        resposta[id] = []

    for turma in turmas_planejadas:
        for tipo in resposta.keys():
            if turma["num_edital_id"] == tipo:
                resposta[tipo].append(turma)

    # print(resposta)
    # print(resposta.values)
    # print(resposta.keys)
    # print(resposta.items)

    for r in resposta:
        date_time_now = datetime.now()
        agora = datetime.strftime(date_time_now, '%Y-%m-%d_%H-%M-%S-%f')
        ano_edital = date_time_now.year

        BASE_DIR = '/home/python/app/outputs'
        ACS_PATH = unidecode(f"{ano_edital}/{resposta[r][0]['escola']}")
        OUTPUT_PATH = os.path.join(BASE_DIR, ACS_PATH)

        if not os.path.exists(OUTPUT_PATH):
            os.umask(0)
            os.makedirs(OUTPUT_PATH, mode=0o777)

        # print(type(r))
        # print(resposta[r])
        # print(r)
        doc1 = DocxTemplate("/home/python/app/templates/edital_template.docx")
        # print(doc1)
        doc1.render({'turmas_planejadas': resposta[r]})
        # print(doc1)
        docx = unidecode(f"{OUTPUT_PATH}/edital_{resposta[r][0]['escola']}_{resposta[r][0]['num_edital']}_{agora}.docx")
        # print(docx)
        doc1.save(docx)
        PDF_NAME = convert_to(docx, OUTPUT_PATH)
        PDF_PATH = os.path.join('editais', ACS_PATH, PDF_NAME)
        print(f'Aquivo de edital gerado: "{PDF_PATH}"')

        ### Rotina para atualizar o path do edital em PDF ###
        engine = get_engine(rede)
        connection = engine.connect()
        statement = text(f"""
                        UPDATE edital_ensino
                        SET
                            pdf = '{PDF_PATH}'
                        WHERE
                            id = {r}
                        """)

        connection.execute(statement=statement)
        connection.commit()
        connection.close()


if __name__ == '__main__':
    worker = Worker()
    print('Worker started')

    while True:
        tasks = worker.fetch_tasks()

        for task in tasks:
            rede = task.variables['nomeRede'].value if 'nomeRede' in task.variables else None
            print(rede)
            criaredital(rede)
            worker.complete_task(task_id=task.id_, variables={})
            print('Inserção realizada com sucesso!')

        time.sleep(30)
