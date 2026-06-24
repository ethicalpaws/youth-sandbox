// 周计划页面交互
(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const STORAGE_KEY = 'week2_tasks';
        const NOTES_KEY = 'week2_notes';
        
        // 获取所有任务复选框
        const checkboxes = document.querySelectorAll('.task-check');
        const totalCount = checkboxes.length;
        document.getElementById('totalCount').innerText = totalCount;
        
        // 加载保存的状态
        function loadSavedState() {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                const states = JSON.parse(saved);
                checkboxes.forEach((cb, index) => {
                    if (states[index]) {
                        cb.checked = true;
                    }
                });
            }
            
            // 加载周记
            const savedNotes = localStorage.getItem(NOTES_KEY);
            if (savedNotes) {
                document.getElementById('weeklyNotes').value = savedNotes;
            }
        }
        
        // 保存状态
        function saveState() {
            const states = Array.from(checkboxes).map(cb => cb.checked);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(states));
            updateProgress();
        }
        
        // 更新进度条
        function updateProgress() {
            const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
            const percent = Math.round((checkedCount / totalCount) * 100);
            document.getElementById('completedCount').innerText = checkedCount;
            document.getElementById('progressPercent').innerText = percent;
            document.getElementById('progressFill').style.width = percent + '%';
        }
        
        // 保存周记
        function saveNotes() {
            const notes = document.getElementById('weeklyNotes').value;
            localStorage.setItem(NOTES_KEY, notes);
            alert('✅ 周记已保存！');
        }
        
        // 绑定事件
        checkboxes.forEach(cb => {
            cb.addEventListener('change', saveState);
        });
        
        document.getElementById('saveWeeklyBtn').addEventListener('click', saveNotes);
        
        // 初始化
        loadSavedState();
        updateProgress();
    });
})();