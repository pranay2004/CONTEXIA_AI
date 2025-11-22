import type { Metadata } from 'next'
import { Plus_Jakarta_Sans } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Toaster } from 'sonner'

const plusJakarta = Plus_Jakarta_Sans({ 
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-plus-jakarta',
})

export const metadata: Metadata = {
  title: 'CONTEXIA - The Content Engine',
  description: 'Unified context-to-content automation platform.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`dark ${plusJakarta.variable}`}>
      <body className="font-sans bg-[#020617] text-white antialiased">
        <Providers>
          {/* Global Background Effects */}
          <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
            <div className="absolute top-0 -left-4 w-96 h-96 bg-indigo-500/10 rounded-full mix-blend-screen filter blur-3xl opacity-30" />
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full mix-blend-screen filter blur-3xl opacity-30" />
          </div>
          
          {children}
          
          <Toaster 
            position="top-right" 
            theme="dark"
            toastOptions={{
              style: {
                background: '#0F172A',
                border: '1px solid rgba(255,255,255,0.1)',
                color: 'white',
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}