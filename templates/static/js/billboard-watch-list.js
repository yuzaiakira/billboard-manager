(function() {
    'use strict';

    function initTabs() {
        var tabPdf = document.getElementById('tab-pdf');
        var tabExcel = document.getElementById('tab-excel');
        var panelPdf = document.getElementById('tab-panel-pdf');
        var panelExcel = document.getElementById('tab-panel-excel');

        if (!tabPdf || !panelPdf || !tabExcel || !panelExcel) return;

        function showTab(tabName) {
            if (tabName === 'pdf') {
                panelPdf.classList.remove('hidden');
                panelExcel.classList.add('hidden');
                panelPdf.setAttribute('aria-hidden', 'false');
                panelExcel.setAttribute('aria-hidden', 'true');
                tabPdf.setAttribute('aria-selected', 'true');
                tabExcel.setAttribute('aria-selected', 'false');
                tabPdf.className = 'tab-trigger btn-hover bg-primary text-white font-medium py-2 px-6 rounded-lg transition duration-300 ring-2 ring-offset-2 ring-primary';
                tabExcel.className = 'tab-trigger btn-hover bg-gray-200 text-gray-700 hover:bg-gray-300 font-medium py-2 px-6 rounded-lg transition duration-300';
            } else {
                panelExcel.classList.remove('hidden');
                panelPdf.classList.add('hidden');
                panelExcel.setAttribute('aria-hidden', 'false');
                panelPdf.setAttribute('aria-hidden', 'true');
                tabExcel.setAttribute('aria-selected', 'true');
                tabPdf.setAttribute('aria-selected', 'false');
                tabExcel.className = 'tab-trigger btn-hover bg-green-600 text-white font-medium py-2 px-6 rounded-lg transition duration-300 ring-2 ring-offset-2 ring-green-600';
                tabPdf.className = 'tab-trigger btn-hover bg-gray-200 text-gray-700 hover:bg-gray-300 font-medium py-2 px-6 rounded-lg transition duration-300';
            }
        }

        tabPdf.addEventListener('click', function() { showTab('pdf'); });
        tabExcel.addEventListener('click', function() { showTab('excel'); });
    }

    function initRemoveFromList() {
        var items = document.getElementsByClassName('button-add-list');
        if (!items.length) return;

        function sendData(obj) {
            if (obj.classList.contains('button-added-list')) return;
            var xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function() {
                if (this.readyState === 4 && this.status === 200) {
                    obj.classList.add('button-added-list');
                    var card = obj.closest('.card-hover');
                    if (card) card.remove();
                }
            };
            xhttp.open('GET', obj.getAttribute('href'));
            xhttp.send();
        }

        for (var i = 0; i < items.length; i++) {
            items[i].addEventListener('click', function(e) {
                e.preventDefault();
                sendData(this);
            });
        }
    }

    function init() {
        initTabs();
        initRemoveFromList();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
