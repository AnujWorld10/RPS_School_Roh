export function hasAnyPermission(
  userPermissions: readonly string[],
  requiredPermissions: readonly string[],
) {
  return requiredPermissions.length === 0
    || requiredPermissions.some((permission) => userPermissions.includes(permission))
}

export function roleLandingPath(roles: readonly string[]) {
  if (roles.includes('SUPER_ADMIN') || roles.includes('ADMIN')) return '/dashboard'
  if (roles.includes('TEACHER')) return '/portal/teacher'
  if (roles.includes('STUDENT')) return '/portal/student'
  if (roles.includes('PARENT')) return '/portal/parent'
  return '/dashboard'
}
