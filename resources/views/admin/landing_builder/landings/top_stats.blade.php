<<<<<<< HEAD
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card card-statistic-2">
            <div class="card-stats">
                <div class="card-stats-title">Total Landing Pages</div>
                <div class="card-stats-items">
                    <div class="card-stats-item">
                        <div class="card-stats-item-count">{{ $totalLandingPages ?? 0 }}</div>
                        <div class="card-stats-item-label">Total</div>
                    </div>
                </div>
            </div>
            <div class="card-icon shadow-primary bg-primary">
                <i class="fa fa-file"></i>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card card-statistic-2">
            <div class="card-stats">
                <div class="card-stats-title">Active Pages</div>
                <div class="card-stats-items">
                    <div class="card-stats-item">
                        <div class="card-stats-item-count">{{ $activeLandingPages ?? 0 }}</div>
                        <div class="card-stats-item-label">Active</div>
                    </div>
                </div>
            </div>
            <div class="card-icon shadow-success bg-success">
                <i class="fa fa-check"></i>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card card-statistic-2">
            <div class="card-stats">
                <div class="card-stats-title">Disabled Pages</div>
                <div class="card-stats-items">
                    <div class="card-stats-item">
                        <div class="card-stats-item-count">{{ $disabledLandingPages ?? 0 }}</div>
                        <div class="card-stats-item-label">Disabled</div>
                    </div>
                </div>
            </div>
            <div class="card-icon shadow-warning bg-warning">
                <i class="fa fa-pause"></i>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card card-statistic-2">
            <div class="card-stats">
                <div class="card-stats-title">Components</div>
                <div class="card-stats-items">
                    <div class="card-stats-item">
                        <div class="card-stats-item-count">{{ $totalLandingComponents ?? 0 }}</div>
                        <div class="card-stats-item-label">Available</div>
                    </div>
                </div>
            </div>
            <div class="card-icon shadow-info bg-info">
                <i class="fa fa-puzzle-piece"></i>
            </div>
        </div>
    </div>
</div>
=======
<div class="row">
    <div class="col-lg-3 col-md-6 col-sm-6 col-12">
        <div class="card-statistic">
            <div class="card-statistic__mask"></div>
            <div class="card-statistic__wrap">
                <div class="d-flex align-items-start justify-content-between">
                    <span class="text-gray-500 mt-8">{{ trans('update.total_landing_pages') }}</span>
                    <div class="d-flex-center size-48 bg-primary-30 rounded-12">
                        <x-iconsax-bul-colorfilter class="icons text-primary" width="24px" height="24px"/>
                    </div>
                </div>

                <h5 class="font-24 mt-12 line-height-1 text-black">{{ $totalLandingPages }}</h5>
            </div>
        </div>
    </div>

    <div class="col-lg-3 col-md-6 col-sm-6 col-12">
        <div class="card-statistic">
            <div class="card-statistic__mask"></div>
            <div class="card-statistic__wrap">
                <div class="d-flex align-items-start justify-content-between">
                    <span class="text-gray-500 mt-8">{{ trans('update.active_landing_pages') }}</span>
                    <div class="d-flex-center size-48 bg-success-30 rounded-12">
                        <x-iconsax-bul-colorfilter class="icons text-success" width="24px" height="24px"/>
                    </div>
                </div>

                <h5 class="font-24 mt-12 line-height-1 text-black">{{ $activeLandingPages }}</h5>
            </div>
        </div>
    </div>

    <div class="col-lg-3 col-md-6 col-sm-6 col-12">
        <div class="card-statistic">
            <div class="card-statistic__mask"></div>
            <div class="card-statistic__wrap">
                <div class="d-flex align-items-start justify-content-between">
                    <span class="text-gray-500 mt-8">{{ trans('update.disabled_landing_pages') }}</span>
                    <div class="d-flex-center size-48 bg-danger-30 rounded-12">
                        <x-iconsax-bul-colorfilter class="icons text-danger" width="24px" height="24px"/>
                    </div>
                </div>

                <h5 class="font-24 mt-12 line-height-1 text-black">{{ $disabledLandingPages }}</h5>
            </div>
        </div>
    </div> 

    <div class="col-lg-3 col-md-6 col-sm-6 col-12">
        <div class="card-statistic">
            <div class="card-statistic__mask"></div>
            <div class="card-statistic__wrap">
                <div class="d-flex align-items-start justify-content-between">
                    <span class="text-gray-500 mt-8">{{ trans('update.landing_components') }}</span>
                    <div class="d-flex-center size-48 bg-info-30 rounded-12">
                        <x-iconsax-bul-category class="icons text-info" width="24px" height="24px"/>
                    </div>
                </div>

                <h5 class="font-24 mt-12 line-height-1 text-black">{{ $totalLandingComponents }}</h5>
            </div>
        </div>
    </div>
</div>
>>>>>>> final_initial_branch
