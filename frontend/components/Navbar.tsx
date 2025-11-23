'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSession, signOut } from 'next-auth/react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Sparkles, Menu, X, User, LogOut, Settings, 
  FileText, TrendingUp, Upload as UploadIcon, ChevronDown
} from 'lucide-react'
import { Button } from '@/components/ui/button'

interface NavbarProps {
  transparent?: boolean
}

export function Navbar({ transparent = false }: NavbarProps) {
  const router = useRouter()
  const { data: session, status } = useSession()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const isLoading = status === 'loading'
  const isAuthenticated = !!session

  const handleLogout = async () => {
    setDropdownOpen(false)
    await signOut({ redirect: true, callbackUrl: '/' })
  }

  const navLinks = [
    { label: 'Dashboard', href: '/dashboard', icon: TrendingUp, auth: true },
  ]

  return (
    <nav className={`sticky top-0 z-50 border-b ${
      transparent 
        ? 'bg-[#0F172A]/80 backdrop-blur-xl border-white/10' 
        : 'bg-[#0F172A]/95 backdrop-blur-md border-white/10'
    }`}>
      <div className="container mx-auto px-4 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <motion.button
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-2 group"
            onClick={() => router.push(isAuthenticated ? '/dashboard' : '/')}
          >
            <div className="w-9 h-9 lg:w-10 lg:h-10 bg-gradient-to-br from-indigo-600 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:shadow-indigo-500/40 transition-shadow">
              <Sparkles className="w-4 h-4 lg:w-5 lg:h-5 text-white" />
            </div>
            <span className="text-xl lg:text-2xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">CONTEXIA</span>
          </motion.button>

          {/* Desktop Navigation */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="hidden md:flex items-center gap-3"
          >
            {/* Nav Links */}
            <div className="flex items-center gap-1">
              {navLinks
                .filter(link => !link.auth || isAuthenticated)
                .map((link) => (
                  <Button
                    key={link.href}
                    variant="ghost"
                    size="sm"
                    className="rounded-xl text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
                    onClick={() => router.push(link.href)}
                  >
                    <link.icon className="w-4 h-4 mr-2" />
                    {link.label}
                  </Button>
                ))}
            </div>

            {!isLoading && (
              <>
                {isAuthenticated ? (
                  // User Menu Dropdown
                  <div className="relative ml-2">
                    <button
                      onClick={() => setDropdownOpen(!dropdownOpen)}
                      className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-white/10 transition-colors border border-white/10"
                    >
                      <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-cyan-500 rounded-lg flex items-center justify-center text-white font-semibold text-sm shadow-lg">
                        {session.user?.name?.charAt(0).toUpperCase() || 'U'}
                      </div>
                      <span className="font-medium text-white hidden lg:block">
                        {session.user?.name || 'User'}
                      </span>
                      <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${
                        dropdownOpen ? 'rotate-180' : ''
                      }`} />
                    </button>

                    <AnimatePresence>
                      {dropdownOpen && (
                        <>
                          <div 
                            className="fixed inset-0 z-40" 
                            onClick={() => setDropdownOpen(false)}
                          />
                          <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="absolute right-0 mt-2 w-56 glass-card rounded-xl shadow-2xl overflow-hidden z-50 border border-white/20"
                          >
                            <div className="p-3 border-b border-white/10 bg-white/5">
                              <p className="font-semibold text-white">{session.user?.name || 'User'}</p>
                              <p className="text-sm text-gray-400">{session.user?.email || ''}</p>
                            </div>
                            <div className="p-2">
                              <button
                                onClick={() => {
                                  setDropdownOpen(false)
                                  router.push('/profile')
                                }}
                                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left"
                              >
                                <User className="w-4 h-4 text-gray-400" />
                                <span className="text-white">Profile</span>
                              </button>
                              <button
                                onClick={() => {
                                  setDropdownOpen(false)
                                  router.push('/dashboard/content')
                                }}
                                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left"
                              >
                                <FileText className="w-4 h-4 text-gray-400" />
                                <span className="text-white">My Content</span>
                              </button>
                              <button
                                onClick={() => {
                                  setDropdownOpen(false)
                                  router.push('/profile?tab=settings')
                                }}
                                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left"
                              >
                                <Settings className="w-4 h-4 text-gray-400" />
                                <span className="text-white">Settings</span>
                              </button>
                            </div>
                            <div className="p-2 border-t border-white/10">
                              <button
                                onClick={handleLogout}
                                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-red-500/10 transition-colors text-left text-red-400"
                              >
                                <LogOut className="w-4 h-4" />
                                <span>Logout</span>
                              </button>
                            </div>
                          </motion.div>
                        </>
                      )}
                    </AnimatePresence>
                  </div>
                ) : (
                  // Auth Buttons
                  <>
                    <Button
                      size="sm"
                      className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/25 rounded-xl px-6"
                      onClick={() => router.push('/login')}
                    >
                      Sign In
                    </Button>
                  </>
                )}
              </>
            )}
          </motion.div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <X className="w-5 h-5 text-gray-300" />
              ) : (
                <Menu className="w-5 h-5 text-gray-300" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden border-t border-slate-200 dark:border-slate-800 mt-4 pt-4 overflow-hidden"
            >
              <div className="space-y-2">
                {navLinks
                  .filter(link => !link.auth || isAuthenticated)
                  .map((link) => (
                    <button
                      key={link.href}
                      onClick={() => {
                        router.push(link.href)
                        setMobileMenuOpen(false)
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left"
                    >
                      <link.icon className="w-4 h-4 text-gray-400" />
                      <span className="text-white">{link.label}</span>
                    </button>
                  ))}

                {!isLoading && (
                  <>
                    {isAuthenticated ? (
                      <>
                        <div className="pt-2 border-t border-white/10">
                          <button
                            onClick={() => {
                              router.push('/profile')
                              setMobileMenuOpen(false)
                            }}
                            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left"
                          >
                            <User className="w-4 h-4 text-gray-400" />
                            <span className="text-white">Profile</span>
                          </button>
                          <button
                            onClick={() => {
                              router.push('/profile?tab=settings')
                              setMobileMenuOpen(false)
                            }}
                            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left"
                          >
                            <Settings className="w-4 h-4 text-gray-400" />
                            <span className="text-white">Settings</span>
                          </button>
                          <button
                            onClick={() => {
                              handleLogout()
                              setMobileMenuOpen(false)
                            }}
                            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-red-500/10 transition-colors text-left text-red-400"
                          >
                            <LogOut className="w-4 h-4" />
                            <span>Logout</span>
                          </button>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="pt-2 border-t border-white/10">
                          <button
                            onClick={() => {
                              router.push('/login')
                              setMobileMenuOpen(false)
                            }}
                            className="w-full mt-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-2 px-4 rounded-xl font-semibold shadow-lg shadow-indigo-500/25"
                          >
                            Sign In
                          </button>
                        </div>
                      </>
                    )}
                    
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  )
}
