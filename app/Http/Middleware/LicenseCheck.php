<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class LicenseCheck
{
    /**
     * Handle an incoming request.
     * This is a bypass version that always allows requests to proceed.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle(Request $request, Closure $next)
    {
        // License check bypassed - always allow request to proceed
        return $next($request);
    }
}