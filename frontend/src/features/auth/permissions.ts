export function hasAnyPermission(
  userPermissions: readonly string[],
  requiredPermissions: readonly string[],
) {
  return requiredPermissions.length === 0
    || requiredPermissions.some((permission) => userPermissions.includes(permission))
}
