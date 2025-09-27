import { createClient } from '@supabase/supabase-js'

// Supabase configuration - these will be exposed to the client
// Make sure SUPABASE_URL and SUPABASE_ANON_KEY are safe for frontend use
const supabaseUrl = window.SUPABASE_URL || 'YOUR_SUPABASE_URL'
const supabaseAnonKey = window.SUPABASE_ANON_KEY || 'YOUR_SUPABASE_ANON_KEY'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

/**
 * Sign in with email and password
 * @param {string} email - User's email
 * @param {string} password - User's password
 * @returns {Promise<{user, session, error}>}
 */
export async function signInWithPassword(email, password) {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    
    if (error) {
      console.error('Sign in error:', error.message)
      return { user: null, session: null, error: error.message }
    }
    
    console.log('Sign in successful:', data.user.email)
    return { user: data.user, session: data.session, error: null }
  } catch (err) {
    console.error('Unexpected sign in error:', err)
    return { user: null, session: null, error: 'An unexpected error occurred' }
  }
}

/**
 * Sign out the current user
 * @returns {Promise<{error}>}
 */
export async function signOut() {
  try {
    const { error } = await supabase.auth.signOut()
    
    if (error) {
      console.error('Sign out error:', error.message)
      return { error: error.message }
    }
    
    console.log('Sign out successful')
    return { error: null }
  } catch (err) {
    console.error('Unexpected sign out error:', err)
    return { error: 'An unexpected error occurred during sign out' }
  }
}

/**
 * Get the current user session
 * @returns {Promise<{user, session}>}
 */
export async function getCurrentSession() {
  try {
    const { data: { session } } = await supabase.auth.getSession()
    return { user: session?.user || null, session }
  } catch (err) {
    console.error('Error getting current session:', err)
    return { user: null, session: null }
  }
}

/**
 * Get user role from metadata
 * @param {Object} user - Supabase user object
 * @returns {string} - User role (student, teacher, etc.)
 */
export function getUserRole(user) {
  if (!user) return null
  
  // Check in raw_user_meta_data first, then user_metadata
  const metadata = user.raw_user_meta_data || user.user_metadata || {}
  return metadata.role || 'student' // default to student if no role found
}

/**
 * Store session token in a cookie for Flask to read
 * @param {Object} session - Supabase session object
 */
export function storeSessionForFlask(session) {
  if (session?.access_token) {
    // Set httpOnly=false so we can access it from JS, but secure in production
    document.cookie = `supabase-token=${session.access_token}; path=/; SameSite=Lax; max-age=3600`
    
    // Also store user info for quick access
    const userInfo = {
      id: session.user.id,
      email: session.user.email,
      role: getUserRole(session.user)
    }
    
    document.cookie = `user-info=${JSON.stringify(userInfo)}; path=/; SameSite=Lax; max-age=3600`
  }
}

/**
 * Clear session cookies
 */
export function clearSessionCookies() {
  document.cookie = 'supabase-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
  document.cookie = 'user-info=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
}

/**
 * Listen to auth state changes
 * @param {Function} callback - Callback function to handle auth state changes
 */
export function onAuthStateChange(callback) {
  return supabase.auth.onAuthStateChange((event, session) => {
    console.log('Auth state changed:', event, session?.user?.email)
    
    if (event === 'SIGNED_IN') {
      storeSessionForFlask(session)
    } else if (event === 'SIGNED_OUT') {
      clearSessionCookies()
    }
    
    callback(event, session)
  })
}

// Export supabase client as default for direct access if needed
export default supabase