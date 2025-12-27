<?php
/**
 * TEMPLATE: Middleware Replacement
 * 
 * Use this for replacing encrypted middleware files.
 * Most middleware just need to pass requests through.
 */

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class EncryptedMiddlewareTemplate
{
    /**
     * Handle an incoming request.
     * 
     * For bypass: Just pass through to next middleware
     * For custom logic: Add your checks here
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle(Request $request, Closure $next)
    {
        // Option 1: Simple pass-through (bypass)
        return $next($request);

        // Option 2: With custom logic
        /*
        if ($this->shouldAllow($request)) {
            return $next($request);
        }

        return redirect('/')->with('error', 'Access denied');
        */
    }

    /**
     * Custom validation logic (if needed)
     */
    protected function shouldAllow(Request $request): bool
    {
        // Your custom logic here
        return true;
    }
}
