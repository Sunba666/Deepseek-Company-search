import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
  meta?: { page: number; limit: number; total: number; totalPages: number };
}

@Injectable()
export class ResponseInterceptor<T> implements NestInterceptor<T, ApiResponse<T>> {
  intercept(context: ExecutionContext, next: CallHandler): Observable<ApiResponse<T>> {
    return next.handle().pipe(
      map((data) => {
        if (data && data.data !== undefined && data.meta !== undefined) {
          return { code: 0, message: 'success', data: data.data, meta: data.meta };
        }
        return { code: 0, message: 'success', data };
      }),
    );
  }
}
