/**
 * Extract a human-readable error message from an Axios error response.
 *
 * The backend can return `detail` in three shapes:
 *   - A plain string  (most routes)
 *   - An array of validation objects: [{field, message, type}, ...]  (422 responses)
 *   - Undefined / null (network errors, 500s with no body)
 *
 * Rendering a non-string React child causes a hard crash, so always go through here.
 *
 * @param {unknown} err  - The caught error (usually an Axios error object)
 * @param {string}  fallback - Shown when no usable detail is found
 * @returns {string}
 */
export function extractErrorMessage(err, fallback = "Something went wrong") {
    const detail = err?.response?.data?.detail;
    if (!detail) return fallback;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
        return detail
            .map((d) => d.message || d.msg || d.type || JSON.stringify(d))
            .join(", ");
    }
    return fallback;
}
