import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
export const cors={ 'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'authorization, x-client-info, apikey, content-type' };
export function db(){ return createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!); }
export function json(body:unknown,status=200){ return new Response(JSON.stringify(body),{status,headers:{...cors,'content-type':'application/json'}}); }
