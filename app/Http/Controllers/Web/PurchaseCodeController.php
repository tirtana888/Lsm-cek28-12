<?php

namespace App\Http\Controllers\Web;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

class PurchaseCodeController extends Controller
{
    /**
     * BYPASSED - Always redirect to home
     */
    public function show()
    {
        // License check bypassed - redirect to home
        return redirect('/');
    }

    /**
     * BYPASSED - Always return success
     */
    public function store(Request $request)
    {
        // License check bypassed - redirect to home
        return redirect('/')->with('success', 'License activated successfully!');
    }
}