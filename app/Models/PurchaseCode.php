<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PurchaseCode extends Model
{
    const TYPE_MAIN = 'main';
    const TYPE_MOBILE = 'mobile';
    const TYPE_PLUGIN = 'plugin';
    const TYPE_THEME = 'theme';

    protected $table = 'purchase_codes';

    protected $fillable = [
        'purchase_code',
        'type',
        'license_type',
    ];

    /**
     * BYPASSED - Always return a valid purchase code
     */
    public static function getPurchaseCode()
    {
        return 'BYPASSED-LICENSE-CODE-12345678';
    }

    /**
     * BYPASSED - Always return 'regular' license type
     */
    public static function getLicenseType()
    {
        return 'regular';
    }

    /**
     * BYPASSED - Return true without checking
     */
    public static function isValid()
    {
        return true;
    }

    /**
     * BYPASSED - Always return true for license check
     */
    public static function checkLicense()
    {
        return true;
    }

    /**
     * BYPASSED - Do nothing
     */
    public static function updatePurchaseCode($code, $type = null, $licenseType = null)
    {
        return true;
    }

    /**
     * BYPASSED - Return valid code
     */
    public static function getMobileAppPurchaseCode()
    {
        return 'BYPASSED-MOBILE-LICENSE';
    }

    /**
     * BYPASSED - Do nothing
     */
    public static function updateMobileAppPurchaseCode($code, $licenseType = null)
    {
        return true;
    }

    /**
     * BYPASSED - Return valid code
     */
    public static function getPluginBundlePurchaseCode()
    {
        return 'BYPASSED-PLUGIN-LICENSE';
    }

    /**
     * BYPASSED - Do nothing
     */
    public static function updatePluginBundlePurchaseCode($code, $licenseType = null)
    {
        return true;
    }

    /**
     * BYPASSED - Return valid code
     */
    public static function getThemeBuilderPurchaseCode()
    {
        return 'BYPASSED-THEME-LICENSE';
    }

    /**
     * BYPASSED - Do nothing
     */
    public static function updateThemeBuilderPurchaseCode($code, $licenseType = null)
    {
        return true;
    }
}