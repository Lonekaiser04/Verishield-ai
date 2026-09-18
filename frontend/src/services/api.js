import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export async function screenDocuments({ documents, documentTypes, personPhoto }) {
  const formData = new FormData()
  documents.forEach((file) => formData.append('documents', file))
  if (documentTypes && documentTypes.length) {
    formData.append('document_types', documentTypes.join(','))
  }
  if (personPhoto) {
    formData.append('person_photo', personPhoto)
  }
  const res = await api.post('/screen', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function detectDocumentType(file) {
  const formData = new FormData()
  formData.append('document', file)
  const res = await api.post('/documents/detect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function listScreenings(limit = 50) {
  const res = await api.get('/screenings', { params: { limit } })
  return res.data
}

export async function getScreening(id) {
  const res = await api.get(`/screenings/${id}`)
  return res.data
}

export async function listDemoScenarios() {
  const res = await api.get('/demo/scenarios')
  return res.data
}

export async function runDemoScenario(scenarioId) {
  const res = await api.post(`/demo/seed/${scenarioId}`)
  return res.data
}

export async function getSystemInfo() {
  const res = await api.get('/system/info')
  return res.data
}

export default api
