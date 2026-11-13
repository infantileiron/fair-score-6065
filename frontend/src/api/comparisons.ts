import {request,post} from './client';
import type {Comparison} from '../types/domain';
export const listComparisons=()=>request<Comparison[]>('/comparisons');
export const createComparison=(data:unknown)=>post<Comparison>('/comparisons',data);
