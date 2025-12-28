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