document.getElementById('uploadForm').onsubmit = async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    document.getElementById('loading').style.display = 'block';

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });

        if (response.ok) {
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const audioElement = document.getElementById('audioElement');
            audioElement.src = audioUrl;
            audioElement.style.display = 'block'; 

            document.getElementById('audioPlayer').style.display = 'block'; 
            document.getElementById('feedback').textContent = 'Áudio gerado com sucesso!';
            document.getElementById('feedback').classList.remove('error');
            document.getElementById('feedback').classList.add('success');
        } else {
            const errorData = await response.json();
            document.getElementById('feedback').textContent = errorData.error || 'Erro ao gerar o áudio.';
            document.getElementById('feedback').classList.remove('success');
            document.getElementById('feedback').classList.add('error');
        }
    } catch (error) {
        document.getElementById('feedback').textContent = 'Erro ao enviar o arquivo.';
        document.getElementById('feedback').classList.remove('success');
        document.getElementById('feedback').classList.add('error');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
};
