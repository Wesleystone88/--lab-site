import type { Handler, HandlerEvent } from '@netlify/functions'

export const handler: Handler = async (event: HandlerEvent) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: JSON.stringify({ message: 'Method not allowed' }) }
  }

  let body: { name: string; email: string; subject?: string; message: string }
  try {
    body = JSON.parse(event.body || '{}')
  } catch {
    return { statusCode: 400, body: JSON.stringify({ message: 'Invalid JSON' }) }
  }

  const { name, email, subject, message } = body

  if (!name || !email || !message) {
    return { statusCode: 400, body: JSON.stringify({ message: 'Name, email, and message are required' }) }
  }

  console.log('Contact form submission:', {
    timestamp: new Date().toISOString(),
    name,
    email,
    subject: subject || 'General',
    message,
  })

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ success: true, message: 'Message received.' }),
  }
}
