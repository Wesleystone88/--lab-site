import type { Handler, HandlerEvent } from '@netlify/functions'

interface AccessRequest {
  name: string
  email: string
  org?: string
  use?: string
  message?: string
}

export const handler: Handler = async (event: HandlerEvent) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: JSON.stringify({ message: 'Method not allowed' }) }
  }

  let body: AccessRequest
  try {
    body = JSON.parse(event.body || '{}')
  } catch {
    return { statusCode: 400, body: JSON.stringify({ message: 'Invalid JSON' }) }
  }

  const { name, email, org, use, message } = body

  if (!name || !email) {
    return { statusCode: 400, body: JSON.stringify({ message: 'Name and email are required' }) }
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    return { statusCode: 400, body: JSON.stringify({ message: 'Invalid email address' }) }
  }

  // Log the request (in production, send via email service or store in DB)
  console.log('Access request received:', {
    timestamp: new Date().toISOString(),
    name,
    email,
    org: org || 'Not provided',
    use: use || 'Not provided',
    message: message || 'Not provided',
  })

  // If you have SendGrid/Mailgun/Resend configured:
  // const SENDGRID_KEY = process.env.SENDGRID_API_KEY
  // if (SENDGRID_KEY) { await sendEmail(...) }

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      success: true,
      message: 'Access request received. We will be in touch.',
    }),
  }
}
