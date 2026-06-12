import api from './api.js'

// envia um documento para o server via POST 
// onUploadProgress: função callback que recebe o progresso do envio

export function uploadDocument(formData, onUploadProgress){
    return api.post('/documents/upload', formData, {
        onUploadProgress
    })
}