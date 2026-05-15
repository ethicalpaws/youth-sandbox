// 检测表脚本
(function() {
    function init() {
        const inputs = document.querySelectorAll('.test-input');
        const baseSpan = document.getElementById('baseScore');
        const totalSpan = document.getElementById('totalScore');
        const ratingSpan = document.getElementById('rating');
        const resetBtn = document.getElementById('resetBtn');

        if (!inputs.length) return;

        // 计算满分
        let baseMax = 0, totalMax = 0;
        inputs.forEach(inp => {
            let max = parseInt(inp.dataset.max) || 0;
            if (inp.dataset.bonus === 'true') {
                totalMax += max;
            } else {
                baseMax += max;
                totalMax += max;
            }
        });
        document.getElementById('baseMax') && (document.getElementById('baseMax').innerText = baseMax);
        document.getElementById('totalMax') && (document.getElementById('totalMax').innerText = totalMax);

        function update() {
            let baseTotal = 0, total = 0;
            inputs.forEach(inp => {
                let val = parseInt(inp.value) || 0;
                if (inp.dataset.bonus === 'true') {
                    total += val;
                } else {
                    baseTotal += val;
                    total += val;
                }
            });
            baseSpan.innerText = baseTotal;
            totalSpan.innerText = total;

            let percent = baseMax ? (baseTotal / baseMax) * 100 : 0;
            let rating = '📘 待加强';
            if (percent >= 90) rating = '🔥 优秀';
            else if (percent >= 75) rating = '✅ 良好';
            else if (percent >= 60) rating = '⚠️ 及格';
            ratingSpan.innerText = rating;
        }

        inputs.forEach(inp => {
            inp.addEventListener('input', function() {
                let val = parseInt(this.value) || 0;
                let max = parseInt(this.dataset.max) || 0;
                if (val > max) this.value = max;
                if (val < 0) this.value = 0;
                update();
            });
        });

        resetBtn && resetBtn.addEventListener('click', () => {
            inputs.forEach(inp => inp.value = 0);
            update();
            const notes = document.getElementById('testNotes');
            if (notes) notes.value = '';
        });

        update();
    }

    // 折叠答案功能
    function initAnswers() {
        const answerBtns = document.querySelectorAll('.answer-btn');
        answerBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const content = this.nextElementSibling;
                if (content && content.classList.contains('answer-content')) {
                    content.classList.toggle('show');
                    this.textContent = content.classList.contains('show') ? '📘 收起答案' : '📖 查看答案';
                }
            });
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        init();
        initAnswers();
    });
})();