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
                url: "/yodachannel/picture_page?page_num=" + hidden_page_num + "&" + "order=" + parsed_order,
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
    let pictures = [];
    let pictures_pictures = [];
    data.pictures.forEach(function (picture, index, array) {
        pictures.push(JSON.parse(picture));
    });
    data.pictures_picture.forEach(function (pictures_picture, index, array) {
        pictures_pictures.push(JSON.parse(pictures_picture));
    });

    // let mails_pictures = JSON.parse(data.mails_pictures);

    if (data.status === 'SUCCESS') {
        // 循环遍历数据并增加到前端页面
        pictures.forEach(function (picture, index, array) {
            let picture_pictures = [];
            pictures_pictures.forEach(function (pictures_picture, index, array) {
                if (pictures_picture[0].fields.weibo === picture[0].pk) {
                    picture_pictures.push(pictures_picture)
                }
            });
            let prev_picture_date = $('.picture-date').last().val();
            let new_picture_html = build_html(picture, picture_pictures, prev_picture_date);
            $('.pictures-container').append(new_picture_html);
        });
        picture_window();
        if (data.has_next === 'true') {
            $('#hidden-page-num').val(data.new_page_num);
        } else {
            $('.pictures-container').append('<div style="text-align: center; color: black; font-weight: bold">已加载全部</div>');
            $('#hidden-page-num').val('#');
        }
    }
}


function build_html(picture, picture_pictures, prev_picture_date) {
    let new_html = '';
    if (picture_pictures.length > 0) {
        if (!is_same_month(prev_picture_date, picture[0].fields.created_at)) {
            new_html += '<hr/>' +
                        '<div class="timeline">' +
                            parse_timeline_time(picture[0].fields.created_at) +
                        '</div>';
        }
        picture_pictures.forEach(function (picture_picture, index, array) {
            new_html += '<a class="picture-container">' +
                            '<div class="picture-picture-container">';
            new_html +=         '<img class="picture-picture" src="/static/yodachannel/images/weibo/' + picture_picture[0].fields.file_name + '">' +
                                '<input type="hidden" class="picture-date" value="' + picture[0].fields.created_at+ '">' +
                            '</div>' +
                        '</a>';
        });
    }
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

function parse_timeline_time(time) {
    let date_time = new Date(time);
    let mm = date_time.getMonth() + 1;
    let yyyy = date_time.getFullYear();
    return yyyy + '.' + mm;
}

function is_same_month(prev, curr) {
    let prev_date = new Date(prev);
    let curr_date = new Date(curr);
    console.log(prev_date, curr_date);
    console.log(prev_date.getFullYear() === curr_date.getFullYear() && (prev_date.getMonth() === curr_date.getMonth()));
    return prev_date.getFullYear() === curr_date.getFullYear() && (prev_date.getMonth() === curr_date.getMonth());
}

window.onscroll = scrollBottomOrTop;

