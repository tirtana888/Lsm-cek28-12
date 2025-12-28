<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class MobileAppLicenseCheck
{
    /**
     * BYPASSED - Always allow requests to proceed
     */
    public function handle(Request $request, Closure $next)
    {
        return $next($request);
    }
}