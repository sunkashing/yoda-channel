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
                url: "/yodachannel/blog_page?page_num=" + hidden_page_num + "&" + "order=" + parsed_order,
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
    let blogs = [];
    data.blogs.forEach(function (blog, index, array) {
        blogs.push(JSON.parse(blog));
    });

    // let blogs_pictures = JSON.parse(data.blogs_pictures);

    if (data.status === 'SUCCESS') {
        // 循环遍历数据并增加到前端页面
        blogs.forEach(function (blog, index, array) {
            let prev_blog_date = $('.blog-date').last().text();
            let new_blog_html = build_html(blog, prev_blog_date);
            $('.blogs-container').append(new_blog_html);
        });
        if (data.has_next === 'true') {
            $('#hidden-page-num').val(data.new_page_num);
        } else {
            $('.blogs-container').append('<div style="text-align: center; color: black; font-weight: bold">已加载全部</div>');
            $('#hidden-page-num').val('#');
        }
    }
}


function build_html(blog, prev_blog_date) {
    let new_html = '';
    if (!is_same_month(prev_blog_date, blog[0].fields.created_at)) {
        new_html += '<hr/>' +
                    '<div class="timeline">' +
                        parse_timeline_time(blog[0].fields.created_at) +
                    '</div>';
    }
    new_html += '<a href="/yodachannel/blog_view/' + blog[0].pk + '">' +
                        '<div class="blog-container">' +
                            '<div class="blog-title-container">' +
                                '<div class="inline">' +
                                    '<div class="blog-title inline">' +
                                        blog[0].fields.blog_title +
                                    '</div>' +
                                    '<div class="blog-info blog-date inline">' +
                                        parse_time(blog[0].fields.created_at) +
                                    '</div>' +
                                '</div>' +
                                '<div class="blog-info weibo-cat inline">' +
                                    'Blog' +
                                '</div>' +
                            '</div>' +
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

