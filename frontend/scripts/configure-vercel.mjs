import { writeFileSync } from 'node:fs';
const raw = process.env.FLUIDMES_BACKEND_URL;
if (!raw) throw new Error('Configure FLUIDMES_BACKEND_URL na Vercel com a URL HTTPS do backend.');
const url = new URL(raw);
if (url.protocol !== 'https:' || url.username || url.password || url.search || url.hash || url.pathname !== '/') {
  throw new Error('FLUIDMES_BACKEND_URL deve conter somente a origem HTTPS do backend.');
}
const origin = url.origin;
writeFileSync('vercel.json', JSON.stringify({
  $schema: 'https://openapi.vercel.sh/vercel.json', framework: 'vite',
  buildCommand: 'npm run build', outputDirectory: 'dist',
  rewrites: [
    {source:'/api/:path*',destination:`${origin}/api/:path*`},
    {source:'/admin',destination:`${origin}/admin/`},
    {source:'/admin/:path*',destination:`${origin}/admin/:path*`},
    {source:'/static/:path*',destination:`${origin}/static/:path*`},
    {source:'/((?!api(?:/|$)|admin(?:/|$)|static(?:/|$)).*)',destination:'/index.html'}
  ], headers: [{source:'/api/:path*',headers:[{key:'Cache-Control',value:'private, no-store'}]},
    {source:'/admin/:path*',headers:[{key:'Cache-Control',value:'private, no-store'}]}]
},null,2)+'\n');
console.log('Rotas de API/admin/static e SPA configuradas em vercel.json.');
