const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function isValidEmail(email: string): boolean {
  return EMAIL_REGEX.test(email.trim())
}

export function validateLogin(email: string, password: string): { email?: string; password?: string } {
  const err: { email?: string; password?: string } = {}
  if (!email.trim()) err.email = 'Email is required'
  else if (!isValidEmail(email)) err.email = 'Invalid email format'
  if (!password) err.password = 'Password is required'
  return err
}

export function validateSignup(
  email: string,
  name: string,
  password: string
): { email?: string; name?: string; password?: string } {
  const err = validateLogin(email, password) as { email?: string; name?: string; password?: string }
  if (!name.trim()) err.name = 'Name is required'
  if (password.length > 0 && password.length < 6) err.password = 'Password must be at least 6 characters'
  return err
}
