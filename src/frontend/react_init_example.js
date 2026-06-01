// React example: initialize Socratic session on component mount
// Place this in your React app and adapt the endpoint URL as needed.

import React, { useEffect, useState } from 'react'

export default function SocraticInitExample() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function init() {
      setLoading(true)
      try {
        const res = await fetch('http://localhost:8000/api/session/init', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ student_id: 'student_123' }),
        })
        const data = await res.json()
        setSession(data)
      } catch (err) {
        console.error('Session init failed', err)
      } finally {
        setLoading(false)
      }
    }

    init()
  }, [])

  if (loading) return <div>Initializing session...</div>
  if (!session) return <div>Not initialized</div>

  return (
    <div>
      <h3>Socratic Session</h3>
      <p>Session ID: {session.session_id}</p>
      <p>Level: {session.studentLevel}</p>
      <p>Strategy: {session.preferredStrategy}</p>
    </div>
  )
}
