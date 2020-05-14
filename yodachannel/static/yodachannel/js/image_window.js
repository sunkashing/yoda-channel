
$(document).ready(function() {
    image_window();
});

function image_window() {
        // 获取弹窗
    let modal = document.getElementById('myModal');

    // 获取图片插入到弹窗 - 使用 "alt" 属性作为文本部分的内容
    let modalImg = document.getElementById("img01");
    $('.mail-picture').click(function () {
        console.log("img clicked.");
        modal.style.display = "block";
        modalImg.src = $(this).attr('src');
    });

    // 获取 <span> 元素，设置关闭按钮
    let span = document.getElementsByClassName("close-image")[0];

    // 当点击 (x), 关闭弹窗
    span.onclick = function () {
        modal.style.display = "none";
    };
}
