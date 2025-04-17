export interface Asset {
  id: string;
  name: string;
  type: string;
  status: string;
  version: number;
  metadata: Record<string, string | number | boolean | null>;
  created_at: string;
  updated_at: string;
}

export interface Shot {
  id: string;
  name: string;
  sequence: string;
  frameStart: number;
  frameEnd: number;
  status: string;
  version: number;
  assets: string[];
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  createdAt: string;
  updatedAt: string;
}

export interface ApiError {
  message: string;
  statusCode: number;
}