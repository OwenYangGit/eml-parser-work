#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from flanker import mime


def CreateHtml(title, addresser, addressee, sendTime, content, annex, path):
    '''
    建立html檔案
    :param title: 標題
    :param addresser: 發件人
    :param addressee: 收件人
    :param sendTime: 傳送時間
    :param content: 內容
    :param annex: 附件
    :param path: 儲存路徑
    :return:
    '''
    # HTML模板

    template = '''
    <!DOCTYPE html>
    <html>

    <head lang="en">
        <meta charset="UTF-8">
        <title>test1</title>
        <link rel="stylesheet" type="text/css" href="../caseView/css/index.css" />
        <link rel="stylesheet" href="../caseView/dist/layui-v2.5.6/layui/css/layui.css">
        <script src="../caseView/dist/jquery.min.js"></script>
        <script src="../caseView/dist/layui-v2.5.6/layui/layui.js" charset="utf-8"></script>
    </head>
   <body>
        <div id="email" class="noOneTop">
            <div id="contentInfo">
                <div class="email">
                    <div class="email_title">
                        <p>%(title)s</p>
                    </div>
                    <div style="clear: both;"></div>
                    <div class="email_info">
                        <p><span>發件人：</span>%(addresser)s</p>
                        <p><span>收件人：</span>%(addressee)s</p>
                        <p><span>傳送時間：</span>%(sendTime)s</p>
                    </div>
                    <div class="email_content" id="email_content">
                        %(content)s
                    </div>
                    <div class="email_file">
                        %(annex)s
                    </div>
                </div>
            </div>
        </div>
    </body>
    <script>
        $("#email_content").html("<meta" + $("#email_content").html().split('<meta')[1])
    </script>
    </html>'''

    if addressee is None:
        addressee = ''
    if sendTime is None:
        sendTime = ''

    data = {'title': title, 'addresser': addresser, 'addressee': addressee, 'sendTime': sendTime,
            'content': content, 'annex': annex}
    html = template % data
    with open(path, 'wb') as file:
        file.write(html.encode())
        file.close()


# 郵件正文
def contentEml(eml):
    # 判斷是否為單部分

    if eml.content_type.is_singlepart():
        eml_body = eml.body
    else:
        eml_body = ''
        for part in eml.parts:
            # 判斷是否是多部分
            if part.content_type.is_multipart():
                eml_body, charset = contentEml(part)
            else:
                if part.content_type.main == 'text':
                    eml_body = part.body

    return eml_body


def ParseEml(raw_email, path):
    with open(raw_email, 'rb') as fhdl:
        raw_email = fhdl.read()
        eml = mime.from_string(raw_email)
        # 主題
        subjece = eml.subject
        # 獲取發信人地址及暱稱
        eml_header_from = eml.headers.get('From')
        # 暱稱
        # eml_from = address.parse(eml_header_from)
        # from_display_name = eml_from.display_name
        # 傳送時間
        eml_time = eml.headers.get('Date')
        # if eml_time is not None:
        #     eml_time = eml_time.replace(',', '')
        #     dates = datetime.strptime(eml_time, '%a %d %b %Y %H:%M:%S %z')
        #     eml_time = dates.strftime("%Y-%m-%d %H:%M:%S")
        # 解析附件列表
        eml_attachs = ';'.join(x.detected_file_name for x in eml.parts if x.detected_file_name)
        if eml_attachs is not None and eml_attachs != '':
            attachs = eml_attachs.split(';')
            eml_attachs = '<p>附件</p>'
            for ats in attachs:
                eml_attachs += '<dl><dt><img src="../caseView/img/file_mail.png"></dt>' \
                               ' <dd title="OPPO_BR_20200707.log">' + ats + '</dd></dl>'
        # 內容
        eml_body = contentEml(eml)

        # 收件人資訊
        eml_to = eml.headers.get('To')
        if eml_to is not None:
            eml_to = eml_to.replace('<', '&lt;').replace('>', '&gt;')

        #  eml_to_addr = address.parse_list(eml_to)
        # 多個地址以;拼接顯示
        # if not type(eml_to_addr) == str:
        #     to_display_name = ';'.join(x.display_name for x in eml_to_addr if x.display_name)
        #     to_address = ';'.join(x.address for x in eml_to_addr if x.address)
        CreateHtml(subjece, eml_header_from, eml_to, eml_time,
                   eml_body, eml_attachs, path)


if __name__ == "__main__":
    ParseEml('01.eml', './new1.html')