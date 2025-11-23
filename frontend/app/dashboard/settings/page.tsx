'use client'

import { useEffect, useState } from 'react'
import { Save, Mic2, Sparkles, UserCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { toast } from 'sonner'
import { userApi, UserProfile } from '@/lib/api/user'

export default function SettingsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  
  const [profile, setProfile] = useState<UserProfile>({
    company_name: '',
    target_audience: '',
    brand_voice: ''
  })

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const user = await userApi.getProfile()
      setProfile(user.profile)
    } catch (error) {
      // Only show error if it's not a 500 server error (those are logged)
      console.debug("Profile load error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setIsSaving(true)
      await userApi.updateProfile(profile)
      toast.success("Settings saved successfully")
    } catch (error) {
      toast.error("Failed to save settings")
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) return <div className="p-8 text-gray-500">Loading settings...</div>

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Configure your global preferences and AI context</p>
        </div>
        <Button onClick={handleSave} disabled={isSaving} className="bg-indigo-600 hover:bg-indigo-500">
          <Save className="w-4 h-4 mr-2" />
          {isSaving ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>

      {/* Brand Identity Section */}
      <div className="glass-panel p-8 rounded-2xl space-y-6">
        <div className="flex items-start gap-4 border-b border-white/5 pb-6">
          <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400">
            <UserCircle className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">Brand Identity</h2>
            <p className="text-sm text-gray-400">Basic information about your entity</p>
          </div>
        </div>

        <div className="grid gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Company / Personal Brand Name</label>
            <Input 
              value={profile.company_name}
              onChange={(e) => setProfile(prev => ({ ...prev, company_name: e.target.value }))}
              className="bg-black/20 border-white/10 h-12 text-white"
              placeholder="e.g. Acme Corp or John Doe"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Target Audience</label>
            <Textarea 
              value={profile.target_audience}
              onChange={(e) => setProfile(prev => ({ ...prev, target_audience: e.target.value }))}
              className="bg-black/20 border-white/10 min-h-[100px] text-white"
              placeholder="Who are you writing for? (e.g. Tech professionals, Fitness enthusiasts...)"
            />
          </div>
        </div>
      </div>

      {/* Brand Voice Section */}
      <div className="glass-panel p-8 rounded-2xl space-y-6">
        <div className="flex items-start gap-4 border-b border-white/5 pb-6">
          <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400">
            <Mic2 className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">Brand Voice (System Prompt)</h2>
            <p className="text-sm text-gray-400">This instruction will be appended to every AI generation to ensure consistency.</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-indigo-500/5 border border-indigo-500/20 text-sm text-indigo-200 flex gap-3">
            <Sparkles className="w-5 h-5 shrink-0 text-indigo-400" />
            <p>
              <strong>Pro Tip:</strong> Describe your tone using adjectives. Example: "Professional yet conversational, authoritative but humble. Use short sentences. Avoid jargon."
            </p>
          </div>

          <Textarea 
            value={profile.brand_voice}
            onChange={(e) => setProfile(prev => ({ ...prev, brand_voice: e.target.value }))}
            className="bg-black/20 border-white/10 min-h-[200px] font-mono text-sm leading-relaxed text-gray-300"
            placeholder="Enter your system instructions here..."
          />
        </div>
      </div>

    </div>
  )
}