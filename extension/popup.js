
document.addEventListener("DOMContentLoaded", function() {
    const btn = document.getElementById("summarise");
    const savePdfBtn = document.getElementById("save-pdf");
    const outputPara = document.getElementById("output");

    btn.addEventListener("click", function() {
        btn.disabled = true;
        btn.innerHTML = "Summarising...";
        chrome.tabs.query({ currentWindow: true, active: true }, function(tabs) {
            var url = tabs[0].url;
            fetch("http://127.0.0.1:5000/summary?url=" + url)
                .then(response => response.text())
                .then(text => {
                    outputPara.innerHTML = text;
                    btn.disabled = false;
                    btn.innerHTML = "Summarise";
                })
                .catch(error => {
                    console.error('Error:', error);
                    outputPara.innerHTML = "An error occurred. Please try again.";
                    btn.disabled = false;
                    btn.innerHTML = "Summarise";
                });
        });
    });


    savePdfBtn.addEventListener("click", function() {
        const pdf = new jsPDF();
        const outputText = outputPara.innerHTML;

        pdf.setFontSize(18);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Youtube Transcript Summary', 10, 20);
        
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'normal');
        pdf.text(' ', 10, 30);

        let lines = pdf.splitTextToSize(outputText, 180);
        let y = 40;
        lines.forEach(line => {
            if (y + 10 > pdf.internal.pageSize.height - 20) { 
                pdf.addPage();
                y = 20; 
            }
            pdf.text(10, y, line);
            y += 10;
        });

        pdf.save("summary.pdf");
    });

});

