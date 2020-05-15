
$(document).ready(function() {
    video_window();
});

function video_window() {
        // 获取弹窗
    let modal = document.getElementById('myModal');

    // 获取图片插入到弹窗 - 使用 "alt" 属性作为文本部分的内容
    let modalVideo = $("#video01").children('source');
    let navBar = document.getElementById("navBar");
    $('.video-container').click(function () {
        modal.style.display = "block";
        navBar.style.display = "none";
        let pic_src = $(this).children('.video-picture-container').children('.video-picture').attr('src');
        modalVideo.attr('src', picture_to_video_src(pic_src));
        $("#video01")[0].load();
    });

    // 获取 <span> 元素，设置关闭按钮
    let span = document.getElementsByClassName("close-video")[0];

    // 当点击 (x), 关闭弹窗
    span.onclick = function () {
        document.getElementById("video01").pause();
        modal.style.display = "none";
        navBar.style.display = "flex";
    };
}

function picture_to_video_src(pic_src) {
    let left = pic_src.substring(0, pic_src.lastIndexOf('/') - 6);
    let right = pic_src.substring(pic_src.lastIndexOf('/') + 1);
    right = right.substring(0, right.length - 3) + 'mp4';
    console.log(right);
    let path = "/yodachannel/video_view/" + right;
    console.log(path);
    return path;
}
