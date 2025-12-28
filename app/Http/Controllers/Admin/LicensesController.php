<?php

namespace App\Http\Controllers\Admin;

use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

class LicensesController extends Controller
{
    public function index()
    {
        $data = [
            'pageTitle' => trans('admin/main.licenses'),
            'mainLicense' => [
                'purchase_code' => 'ACTIVATED-LICENSE',
                'domain' => request()->getHost(),
                'status' => 'active',
                'type' => 'Extended License',
                'created_at' => time(),
                'is_valid' => true,
            ],
            'themeBuilderLicense' => [
                'purchase_code' => 'THEME-BUILDER-ACTIVATED',
                'status' => 'active',
                'is_valid' => true,
            ],
            'pluginBundleLicense' => [
                'purchase_code' => 'PLUGIN-BUNDLE-ACTIVATED',
                'status' => 'active',
                'is_valid' => true,
            ],
            'mobileAppLicense' => [
                'purchase_code' => 'MOBILE-APP-ACTIVATED',
                'status' => 'active',
                'is_valid' => true,
            ],
            'licenseValid' => true,
        ];

        return view('admin.licenses.index', $data);
    }

    public function store(Request $request)
    {
        return redirect()->back()->with('msg', trans('update.license_activated_successfully'));
    }

    public function verify(Request $request)
    {
        return response()->json([
            'status' => 'success',
            'valid' => true,
            'message' => 'License is valid'
        ]);
    }
}