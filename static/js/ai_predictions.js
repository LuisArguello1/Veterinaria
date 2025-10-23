/**
 * ai_predictions.js - Módulo para la predicción de IA de mascotas
 * 
 * Este módulo maneja las predicciones de IA para mascotas incluyendo:
 * - Predicción de raza
 * - Predicción de etapa de vida
 * - Predicción de condición corporal
 */

// Namespace para las funciones de IA
const AIPredictions = (function() {
    
    // Configuración
    const config = {
        predictionUrl: '/api/predict-image/',
        confidenceThreshold: 70 // Umbral de confianza para considerar una predicción válida
    };
    
    // Estado interno
    let _currentPredictions = null;
    
    /**
     * Realiza predicciones de IA con una imagen
     * @param {File|Blob} imageFile - Archivo o Blob de imagen para predecir
     * @param {Function} onSuccess - Callback para éxito con resultado
     * @param {Function} onError - Callback para errores
     * @param {Function} onStart - Callback al inicio del proceso (opcional)
     * @param {Function} onFinish - Callback al finalizar (opcional)
     */
    function predictImage(imageFile, onSuccess, onError, onStart, onFinish) {
        if (!imageFile) {
            if (onError) onError("No se ha seleccionado ninguna imagen");
            return;
        }
        
        // Iniciar el proceso
        if (onStart) onStart();
        
        // Crear FormData para enviar la imagen
        const formData = new FormData();
        formData.append('image', imageFile);
        
        // Obtener token CSRF
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        // Para depuración: Mostrar qué imagen estamos enviando
        console.log('Enviando imagen para predicción:', {
            tipo: imageFile.type, 
            tamaño: imageFile.size,
            nombre: imageFile.name,
            csrfTokenPresente: !!csrfToken
        });
        
        // Realizar solicitud fetch
        fetch(config.predictionUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            // Verificar si la respuesta es válida antes de intentar parsearla como JSON
            if (!response.ok) {
                console.error('Error en respuesta del servidor:', response.status, response.statusText);
            }
            
            // Si esperamos JSON pero recibimos HTML, esto podría fallar
            return response.text().then(text => {
                try {
                    return JSON.parse(text);
                } catch (e) {
                    console.error('Error al parsear respuesta como JSON:', e);
                    console.log('Contenido de la respuesta:', text.substring(0, 500) + '...'); // Mostrar parte de la respuesta
                    throw new Error('Respuesta no válida del servidor');
                }
            });
        })
        .then(data => {
            if (data && data.success) {
                // Guardar predicciones para uso futuro
                _currentPredictions = data.predictions;
                if (onSuccess) onSuccess(data.predictions);
            } else {
                console.error('Respuesta de error del servidor:', data);
                if (onError) onError(data && data.error ? data.error : "Error en predicción: respuesta del servidor inválida");
            }
        })
        .catch(error => {
            console.error('Error en predicción de IA:', error);
            if (onError) onError("Error de conexión al servicio de predicción");
        })
        .finally(() => {
            if (onFinish) onFinish();
        });
    }
    
    /**
     * Formatea el resultado de una predicción para mostrar
     * @param {Object} prediction - Objeto de predicción individual (breed, stage o body_condition)
     * @returns {Object} - Objeto con datos formateados para mostrar
     */
    function formatPredictionResult(prediction) {
        if (!prediction) return null;
        
        const confidence = prediction.confidence_percentage;
        const isConfident = confidence >= config.confidenceThreshold;
        
        return {
            displayName: prediction.display_name, // Siempre mostrar la predicción, incluso con baja confianza
            confidence: confidence,
            confidenceText: `Confianza: ${confidence}%${!isConfident ? ' (baja)' : ''}`,
            isValid: true, // Considerar todas las predicciones como válidas para mostrarlas
            statusIcon: isConfident ? 
                '<i class="fas fa-check-circle text-green-500 mr-1"></i>' : 
                '<i class="fas fa-exclamation-triangle text-yellow-500 mr-1"></i>',
            statusText: isConfident ? 
                'Predicción confiable' : 
                `Confianza baja (menor al ${config.confidenceThreshold}%)`,
            rawValue: prediction.predicted
        };
    }
    
    /**
     * Obtiene las predicciones actuales
     * @returns {Object|null} - Predicciones actuales o null
     */
    function getCurrentPredictions() {
        return _currentPredictions;
    }
    
    /**
     * Limpia las predicciones almacenadas
     */
    function clearPredictions() {
        _currentPredictions = null;
    }
    
    /**
     * Renderiza las predicciones en contenedores especificados
     * @param {Object} predictions - Objeto de predicciones
     * @param {Object} containers - Objeto con selectores o elementos donde mostrar las predicciones
     */
    function renderPredictions(predictions, containers) {
        if (!predictions) return;
        
        // Predicción de raza
        if (predictions.breed && containers.breed) {
            const breedResult = formatPredictionResult(predictions.breed);
            const breedContainer = typeof containers.breed === 'string' ? 
                document.querySelector(containers.breed) : containers.breed;
                
            if (breedContainer) {
                const resultElement = breedContainer.querySelector('[data-result]');
                const confidenceElement = breedContainer.querySelector('[data-confidence]');
                const statusElement = breedContainer.querySelector('[data-status]');
                
                if (resultElement) resultElement.textContent = breedResult.displayName;
                if (confidenceElement) confidenceElement.textContent = breedResult.confidenceText;
                if (statusElement) statusElement.innerHTML = breedResult.statusIcon + breedResult.statusText;
                
                // Cambiar estilo según confianza (mostrar siempre, pero con colores diferentes)
                const confidence = breedResult.confidence;
                if (confidence >= 70) {
                    breedContainer.className = 'mb-3 p-3 bg-green-50 rounded-lg border border-green-200';
                } else if (confidence >= 50) {
                    breedContainer.className = 'mb-3 p-3 bg-blue-50 rounded-lg border border-blue-200'; // Color original
                } else {
                    breedContainer.className = 'mb-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200';
                }
                
                breedContainer.classList.remove('hidden');
            }
        }
        
        // Predicción de etapa de vida
        if (predictions.stage && containers.stage) {
            const stageResult = formatPredictionResult(predictions.stage);
            const stageContainer = typeof containers.stage === 'string' ? 
                document.querySelector(containers.stage) : containers.stage;
                
            if (stageContainer) {
                const resultElement = stageContainer.querySelector('[data-result]');
                const confidenceElement = stageContainer.querySelector('[data-confidence]');
                const statusElement = stageContainer.querySelector('[data-status]');
                
                if (resultElement) resultElement.textContent = stageResult.displayName;
                if (confidenceElement) confidenceElement.textContent = stageResult.confidenceText;
                if (statusElement) statusElement.innerHTML = stageResult.statusIcon + stageResult.statusText;
                
                // Cambiar estilo según confianza (mostrar siempre, pero con colores diferentes)
                const confidence = stageResult.confidence;
                if (confidence >= 70) {
                    stageContainer.className = 'mb-3 p-3 bg-green-50 rounded-lg border border-green-200';
                } else if (confidence >= 50) {
                    stageContainer.className = 'mb-3 p-3 bg-green-50 rounded-lg border border-green-200'; // Color original
                } else {
                    stageContainer.className = 'mb-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200';
                }
                
                stageContainer.classList.remove('hidden');
            }
        }
        
        // Predicción de condición corporal
        if (predictions.body_condition && containers.bodyCondition) {
            const bodyResult = formatPredictionResult(predictions.body_condition);
            const bodyContainer = typeof containers.bodyCondition === 'string' ? 
                document.querySelector(containers.bodyCondition) : containers.bodyCondition;
                
            if (bodyContainer) {
                const resultElement = bodyContainer.querySelector('[data-result]');
                const confidenceElement = bodyContainer.querySelector('[data-confidence]');
                const statusElement = bodyContainer.querySelector('[data-status]');
                
                if (resultElement) resultElement.textContent = bodyResult.displayName;
                if (confidenceElement) confidenceElement.textContent = bodyResult.confidenceText;
                if (statusElement) statusElement.innerHTML = bodyResult.statusIcon + bodyResult.statusText;
                
                // Siempre mostrar según el valor de la condición, independientemente de la confianza
                const condition = bodyResult.rawValue;
                const confidence = bodyResult.confidence;
                
                // Colores según la condición corporal, pero matizados por la confianza
                if (condition === 'normal') {
                    if (confidence >= 70) {
                        bodyContainer.className = 'mb-3 p-3 bg-green-50 rounded-lg border border-green-200';
                    } else {
                        bodyContainer.className = 'mb-3 p-3 bg-green-50 rounded-lg border border-green-200 opacity-90';
                    }
                } else if (condition === 'delgado') {
                    if (confidence >= 70) {
                        bodyContainer.className = 'mb-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200';
                    } else {
                        bodyContainer.className = 'mb-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200 opacity-90';
                    }
                } else { // obeso
                    if (confidence >= 70) {
                        bodyContainer.className = 'mb-3 p-3 bg-purple-50 rounded-lg border border-purple-200'; // Cambiado a púrpura para coincidir con el HTML
                    } else {
                        bodyContainer.className = 'mb-3 p-3 bg-purple-50 rounded-lg border border-purple-200 opacity-90';
                    }
                }
                
                bodyContainer.classList.remove('hidden');
            }
        }
    }
    
    // API pública
    return {
        predict: predictImage,
        getCurrentPredictions,
        clearPredictions,
        renderPredictions,
        formatPredictionResult
    };
})();

// Exportar para uso en otros archivos si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIPredictions;
}