// Funcionamiento del sistema de identificación del chatbot

/**
 * El chatbot utiliza un sistema de identificación basado en JWT (JSON Web Token)
 * para reconocer al usuario y proporcionar respuestas personalizadas.
 * 
 * Flujo de funcionamiento:
 * 1. Cuando el usuario inicia sesión, cargamos el script chatbot.js
 * 2. Este script solicita un token JWT al servidor mediante una petición a /api/get-chatbot-token/
 * 3. El servidor genera un token con información del usuario y sus mascotas
 * 4. El script envía este token al chatbot usando window.chatbase('identify', { token })
 * 5. El chatbot utiliza esta información para personalizar sus respuestas
 * 
 * NOTA IMPORTANTE:
 * Para que el chatbot utilice la información del usuario, es necesario configurar 
 * la "Context Memory" en el panel de administración de Chatbase. Ver la documentación
 * en docs/chatbot_configuracion_chatbase.md
 */

// Función para obtener el token de identificación del usuario
async function getUserToken() {
    try {
        const response = await fetch('/api/get-chatbot-token/');
        if (!response.ok) {
            throw new Error('Error al obtener token');
        }
        const data = await response.json();
        console.log('Token obtenido correctamente');
        return data.token;
    } catch (error) {
        console.error('Error obteniendo token para chatbot:', error);
        return null;
    }
}

// Función para verificar y depurar el chatbot
async function debugChatbot() {
    try {
        const response = await fetch('/api/get-chatbot-token/');
        if (!response.ok) {
            console.error('Error en la API:', response.status, response.statusText);
            return;
        }
        const data = await response.json();
        console.log('Datos del usuario:', data);
        
        // Decodificar el token JWT para ver su contenido
        const tokenParts = data.token.split('.');
        if (tokenParts.length === 3) {
            const payload = JSON.parse(atob(tokenParts[1]));
            console.log('Información del usuario en el token:', payload);
            
            if (payload.mascotas) {
                console.log('Mascotas encontradas:', payload.mascotas.length);
                console.log('Datos de la primera mascota:', payload.mascotas[0]);
            } else {
                console.log('No se encontraron mascotas en el token');
            }
        }
    } catch (error) {
        console.error('Error depurando chatbot:', error);
    }
}

// Identificar al usuario cuando el chatbot se haya cargado
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Inicializando chatbot...');
    
    // Depurar el chatbot primero
    await debugChatbot();
    
    // Esperar a que el chatbot esté disponible
    const checkChatbase = setInterval(() => {
        if (window.chatbase) {
            clearInterval(checkChatbase);
            console.log('Chatbase detectado, identificando usuario...');
            
            // Obtener token y identificar al usuario
            getUserToken().then(token => {
                if (token) {
                    try {
                        window.chatbase('identify', { token });
                        console.log('Usuario identificado en el chatbot correctamente');
                        
                        // Añadir mensaje de éxito visible
                        const successMsg = document.createElement('div');
                        successMsg.style.position = 'fixed';
                        successMsg.style.bottom = '80px';
                        successMsg.style.right = '20px';
                        successMsg.style.background = '#4CAF50';
                        successMsg.style.color = 'white';
                        successMsg.style.padding = '10px 20px';
                        successMsg.style.borderRadius = '4px';
                        successMsg.style.zIndex = '9999';
                        successMsg.style.opacity = '0.9';
                        successMsg.textContent = 'Chatbot conectado correctamente';
                        document.body.appendChild(successMsg);
                        
                        // Quitar el mensaje después de 3 segundos
                        setTimeout(() => {
                            successMsg.style.opacity = '0';
                            successMsg.style.transition = 'opacity 0.5s';
                            setTimeout(() => successMsg.remove(), 500);
                        }, 3000);
                    } catch (e) {
                        console.error('Error al identificar usuario en chatbase:', e);
                    }
                }
            });
        }
    }, 1000);
});