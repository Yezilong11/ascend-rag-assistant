export interface SuccessResponse<T> {
  success: true
  data: T
}

export interface ErrorResponse {
  success: false
  message: string
}

export type ApiResponse<T> = SuccessResponse<T> | ErrorResponse

export interface MessageOnlyResponse {
  success: true
  message: string
}
