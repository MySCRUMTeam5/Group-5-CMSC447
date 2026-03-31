import { SignUp } from '@clerk/clerk-react'
import './AuthPage.css'

export default function SignUpPage({ navigate }) {
    return (
        <div className="auth-page">
            <div className="auth-brand" onClick={() => navigate('home')} style={{ cursor: 'pointer' }}>
                <div className="auth-brand-icon">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                        <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M9 22V12h6v10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </div>
                <span className="auth-brand-name">HoardHero</span>
            </div>

            <div className="auth-card">
                <SignUp
                    appearance={{
                        elements: {
                            rootBox: 'clerk-root',
                            card: 'clerk-card',
                        },
                    }}
                    signInUrl="#"
                    afterSignUpUrl="/"
                />
                <p className="auth-switch">
                    Already have an account?{' '}
                    <button className="auth-link" onClick={() => navigate('signin')}>
                        Sign in
                    </button>
                </p>
            </div>
        </div>
    )
}
