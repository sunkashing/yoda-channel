function scrollBottomOrTop() {
    let clients = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    let scrollTop = document.documentElement.scrollTop;
    // 这里存在兼容问题，会把body当成div来处理，如果用document.body.scrollHeight就得不到正确的高度，用body时需要把doctype后面的html去掉
    // 这里没用body，而是用到documentElement
    let wholeHeight = document.documentElement.scrollHeight;
    if (clients + scrollTop >= wholeHeight) {
        let hidden_page_num = $('#hidden-page-num').val();
        let parsed_num = parseInt(hidden_page_num, 10);
        let order = $.trim($('.side-bar-active').text());
        let parsed_order = 'new';
        if (order === '最旧') {
            parsed_order = 'old';
        }
        if (!isNaN(parsed_num)) {
            $.ajax({
                url: "/yodachannel/mail_page?page_num=" + hidden_page_num + "&" + "order=" + parsed_order,
                dataType: "json",
                success: update
            });
        }
    }
    // if (scrollTop == 0) {
    //     alert("我到顶部了");
    // }
}

function update(data) {
    let mails = [];
    let mails_pictures = [];
    data.mails.forEach(function (mail, index, array) {
        mails.push(JSON.parse(mail));
    });
    data.mails_pictures.forEach(function (mails_picture, index, array) {
        mails_pictures.push(JSON.parse(mails_picture));
    });

    // let mails_pictures = JSON.parse(data.mails_pictures);

    if (data.status === 'SUCCESS') {
        // 循环遍历数据并增加到前端页面
        mails.forEach(function (mail, index, array) {
            let mail_pictures = [];
            mails_pictures.forEach(function (mails_picture, index, array) {
                if (mails_picture[0].fields.weibo === mail[0].pk) {
                    mail_pictures.push(mails_picture)
                }
            });
            let new_mail_html = build_html(mail, mail_pictures);
            $('.mails-container').append(new_mail_html);
        });
        if (data.has_next === 'true') {
            $('#hidden-page-num').val(data.new_page_num);
        } else {
            $('#hidden-page-num').val('#');
        }
    }
}

function build_mail(mail, index, array, mails_pictures) {

}

function build_html(mail, mail_pictures) {
    let new_html = '<div class="mail-container">' +
                '<a>' +
                    '<div class="mail-title-container">' +
                        '<div class="inline">' +
                            '<div class="mail-title inline">' +
                                mail[0].fields.mail_title +
                            '</div>' +
                            '<div class="mail-info mail-date inline">' +
                                parse_time(mail[0].fields.created_at) +
                            '</div>' +
                        '</div>' +
                        '<div class="mail-info weibo-cat inline">' +
                            'Mail' +
                        '</div>' +
                    '</div>' +
                    '<hr>' +
                    '<div style="padding: 10px 30px;">' +
                        '<div class="mail-text">' +
                            mail[0].fields.mail_text +
                        '</div>' +
                    '</div>' +
                '</a>';
    if (mail_pictures.length > 0) {
        new_html += '<hr>' +
                    '<div class="mail-pictures-container">';
        mail_pictures.forEach(function (mail_picture, index, array) {
            new_html += '<div class="mail-picture_container inline">' +
                            '<img src="/static/yodachannel/images/weibo/' + mail_picture[0].fields.file_name + '">' +
                        '</div>';
        });
        new_html += '</div>';
    }
    new_html += '</div>';
    return new_html
}

function parse_time(time) {
    let date_time = new Date(time);
    let dd = date_time.getDate();
    let mm = date_time.getMonth() + 1;
    let yyyy = date_time.getFullYear();
    let hh = date_time.getHours();
    return yyyy + '/' + mm + '/' + dd
}

window.onscroll = scrollBottomOrTop;
