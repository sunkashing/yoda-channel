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
                url: "/yodachannel/video_page?page_num=" + hidden_page_num + "&" + "order=" + parsed_order,
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
    let videos = [];
    let videos_pictures = [];
    data.videos.forEach(function (video, index, array) {
        videos.push(JSON.parse(video));
    });
    data.videos_video.forEach(function (videos_picture, index, array) {
        videos_pictures.push(JSON.parse(videos_picture));
    });

    // let mails_pictures = JSON.parse(data.mails_pictures);

    if (data.status === 'SUCCESS') {
        // 循环遍历数据并增加到前端页面
        videos.forEach(function (video, index, array) {
            let video_pictures = [];
            videos_pictures.forEach(function (videos_picture, index, array) {
                if (videos_picture[0].fields.weibo === video[0].pk) {
                    video_pictures.push(videos_picture)
                }
            });
            let prev_video_date = $('.video-date').last().val();
            let new_video_html = build_html(video, video_pictures, prev_video_date);
            $('.videos-container').append(new_video_html);
        });
        video_window();
        if (data.has_next === 'true') {
            $('#hidden-page-num').val(data.new_page_num);
        } else {
            $('.pictures-container').append('<div style="text-align: center; color: black; font-weight: bold">已加载全部</div>');
            $('#hidden-page-num').val('#');
        }
    }
}


function build_html(video, video_pictures, prev_video_date) {
    let new_html = '';
    if (!is_same_month(prev_video_date, video[0].fields.created_at)) {
        new_html += '<hr/>' +
                    '<div class="timeline">' +
                        parse_timeline_time(video[0].fields.created_at) +
                    '</div>';
    }
    new_html += '<a class="video-container">' +
                        '<div class="video-picture-container">';
    if (video_pictures.length > 0) {
        video_pictures.forEach(function (video_picture, index, array) {
            new_html += '<img class="video-picture" src="/static/yodachannel/videos/weibo/images/' + video_picture[0].fields.picture_file_name + '">' +
                            '<input type="hidden" class="video-date" value="' + video[0].fields.created_at+ '">'
        });
    }
    new_html += '</div>' +
                '<div class="video-title-container">' +
                    video[0].fields.video_title +
                '</div>' +
            '</a>';
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

