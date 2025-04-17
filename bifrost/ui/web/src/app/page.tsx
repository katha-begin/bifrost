'use client';
import Link from 'next/link';
import { useAssets } from '../services/assetService';
import { useShots } from '../services/shotService';

export default function Home() {
  const { data: assets, isLoading: assetsLoading } = useAssets();
  const { data: shots, isLoading: shotsLoading } = useShots();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Production Overview</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Assets Overview */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Assets</h2>
          {assetsLoading ? (
            <p>Loading assets...</p>
          ) : (
            <div className="space-y-4">
              <p className="text-2xl font-bold">{assets?.length || 0}</p>
              <p className="text-gray-600">Total Assets</p>
              <Link href="/assets" className="btn-primary inline-block">
                View All Assets
              </Link>
            </div>
          )}
        </div>

        {/* Shots Overview */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Shots</h2>
          {shotsLoading ? (
            <p>Loading shots...</p>
          ) : (
            <div className="space-y-4">
              <p className="text-2xl font-bold">{shots?.length || 0}</p>
              <p className="text-gray-600">Total Shots</p>
              <Link href="/shots" className="btn-primary inline-block">
                View All Shots
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card mt-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {assets?.slice(0, 5).map((asset) => (
            <div key={asset.id} className="flex items-center justify-between py-2 border-b">
              <div>
                <p className="font-medium">{asset.name}</p>
                <p className="text-sm text-gray-500">Asset updated</p>
              </div>
              <span className="text-sm text-gray-500">
                {new Date(asset.updated_at).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
